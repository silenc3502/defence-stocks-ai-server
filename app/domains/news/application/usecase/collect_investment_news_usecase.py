"""투자 워크플로우용 뉴스 수집 + 본문 추출 + 양방향 DB 저장 UseCase.

흐름:
  1. SERP API 로 keyword 관련 뉴스 목록 조회
  2. 각 뉴스 링크에 대해:
     a. ArticleContentFetcher 로 본문 추출
     b. MySQL `investment_news` 에 메타데이터 저장 → id 획득
     c. PostgreSQL `investment_news_contents` 에 본문 JSONB 저장 (id 동기화)
     d. PG 저장 실패 시 MySQL 메타데이터 롤백
  3. 부분 실패 허용: 한 뉴스의 fetch/save 가 실패해도 나머지는 계속 진행

재사용 위치:
  - investment 도메인 Retrieval Agent 의 news_source.fetch_news
  - 향후 news 도메인 자체 API 또는 배치 작업
"""
import logging
import traceback
from typing import Optional

from app.domains.news.adapter.outbound.external.article_content_fetcher import (
    ArticleContentFetcher,
)
from app.domains.news.adapter.outbound.external.news_search_port import NewsSearchPort
from app.domains.news.adapter.outbound.persistence.investment_news_content_repository import (
    InvestmentNewsContentRepository,
)
from app.domains.news.adapter.outbound.persistence.investment_news_repository import (
    InvestmentNewsRepository,
)
from app.domains.news.application.response.collect_investment_news_response import (
    CollectedInvestmentNewsItem,
    CollectInvestmentNewsResponse,
)

logger = logging.getLogger(__name__)


class CollectInvestmentNewsUseCase:
    def __init__(
        self,
        news_search_port: NewsSearchPort,
        content_fetcher: ArticleContentFetcher,
        news_repository: InvestmentNewsRepository,
        content_repository: InvestmentNewsContentRepository,
    ):
        self.news_search_port = news_search_port
        self.content_fetcher = content_fetcher
        self.news_repository = news_repository
        self.content_repository = content_repository

    def execute(
        self,
        keyword: str,
        max_results: int = 5,
        original_keyword: Optional[str] = None,
    ) -> CollectInvestmentNewsResponse:
        """
        :param keyword: 실제 SERP 에 전달할 검색 쿼리 (fallback 적용 후)
        :param max_results: 본문 수집 최대 건수
        :param original_keyword: 원본 종목명 (메타데이터 보관용, 없으면 None)
        """
        print(f"  [뉴스] CollectInvestmentNewsUseCase 시작 (keyword={keyword!r})")

        # 1. SERP 검색 (NewsSearchPort.search → (List[NewsItem], total_count))
        searched_items, total = self.news_search_port.search(
            keyword=keyword, page=1, page_size=max_results
        )
        print(f"  [뉴스] SERP 응답: total={total}, 처리할 items={len(searched_items)}건")

        items: list[CollectedInvestmentNewsItem] = []
        failure_count = 0

        for i, news in enumerate(searched_items):
            print(f"  [뉴스] #{i + 1} 처리 시작 — {news.title[:60]}")

            # 2a. 본문 fetch
            try:
                fetched = self.content_fetcher.fetch(news.link)
            except Exception as exc:
                print(f"  [뉴스] #{i + 1} ❌ 본문 fetch 실패, 건너뜀: {exc}")
                logger.warning("뉴스 본문 fetch 실패 (link=%s): %s", news.link, exc)
                failure_count += 1
                continue

            # 2b. MySQL 메타데이터 저장
            try:
                news_id = self.news_repository.save(
                    keyword=original_keyword,
                    query_used=keyword,
                    title=news.title,
                    source=news.source,
                    link=news.link,
                    published_at=news.published_at,
                )
            except Exception as exc:
                print(f"  [뉴스] #{i + 1} ❌ MySQL 저장 실패: {exc}")
                print(traceback.format_exc())
                failure_count += 1
                continue

            # 2c. PostgreSQL 본문 저장
            try:
                self.content_repository.save(
                    news_id=news_id,
                    link=news.link,
                    raw=fetched,
                )
            except Exception as exc:
                print(f"  [뉴스] #{i + 1} ❌ PG 저장 실패, MySQL 롤백 시도: {exc}")
                print(traceback.format_exc())
                self._rollback_metadata(news_id)
                failure_count += 1
                continue

            content_text = fetched.get("text") or ""
            items.append(
                CollectedInvestmentNewsItem(
                    id=news_id,
                    title=news.title,
                    source=news.source,
                    link=news.link,
                    published_at=news.published_at,
                    content=content_text,
                )
            )
            print(f"  [뉴스] #{i + 1} ✅ 저장 성공 (id={news_id}, content={len(content_text)}자)")

        success_count = len(items)
        print(
            f"  [뉴스] 완료: 성공 {success_count}건, 실패 {failure_count}건 "
            f"(SERP 총 {total}건)"
        )

        return CollectInvestmentNewsResponse(
            keyword=original_keyword,
            query_used=keyword,
            items=items,
            total_searched=total,
            success_count=success_count,
            failure_count=failure_count,
        )

    def _rollback_metadata(self, news_id: int) -> None:
        try:
            self.news_repository.delete(news_id)
            print(f"  [뉴스] MySQL 메타데이터 롤백 완료 (id={news_id})")
        except Exception:
            logger.critical(
                "뉴스 메타데이터 롤백 실패 (news_id=%s). 수동 정리 필요.",
                news_id,
                exc_info=True,
            )
