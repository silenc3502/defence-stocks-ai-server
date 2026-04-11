import logging

from sqlalchemy.exc import IntegrityError

from app.domains.news.adapter.outbound.external.article_content_fetcher import (
    ArticleContentFetcher,
)
from app.domains.news.adapter.outbound.persistence.interest_article_content_repository import (
    InterestArticleContentRepository,
)
from app.domains.news.adapter.outbound.persistence.interest_article_repository import (
    InterestArticleRepository,
)
from app.domains.news.application.exceptions import (
    DuplicateInterestArticleError,
    InterestArticleContentPersistError,
)
from app.domains.news.application.request.save_interest_article_request import (
    SaveInterestArticleRequest,
)
from app.domains.news.application.response.save_interest_article_response import (
    SaveInterestArticleResponse,
)

logger = logging.getLogger(__name__)


class SaveInterestArticleUseCase:
    def __init__(
        self,
        article_repository: InterestArticleRepository,
        content_repository: InterestArticleContentRepository,
        content_fetcher: ArticleContentFetcher,
    ):
        self.article_repository = article_repository
        self.content_repository = content_repository
        self.content_fetcher = content_fetcher

    def execute(
        self,
        request: SaveInterestArticleRequest,
        account_id: int,
    ) -> SaveInterestArticleResponse:
        # 1. 중복 저장 차단 (선행 체크)
        if self.article_repository.exists(account_id, request.link):
            raise DuplicateInterestArticleError("이미 저장된 기사입니다.")

        # 2. 원문 fetch — 실패 시 DB 쓰기 전이므로 롤백 불필요
        #    (ArticleFetchError 는 Router 가 502 로 변환)
        fetched = self.content_fetcher.fetch(request.link)

        # 3. MySQL 메타데이터 저장
        try:
            article_id = self.article_repository.save(
                account_id=account_id,
                title=request.title,
                source=request.source,
                link=request.link,
                published_at=request.published_at,
            )
        except IntegrityError as exc:
            # UniqueConstraint 안전망 (선행 체크와 실제 커밋 사이의 race)
            raise DuplicateInterestArticleError("이미 저장된 기사입니다.") from exc

        # 4. PostgreSQL JSONB 에 메타 + fetch 결과 저장
        raw_payload = {
            "metadata": {
                "title": request.title,
                "source": request.source,
                "link": request.link,
                "published_at": (
                    request.published_at.isoformat() if request.published_at else None
                ),
            },
            "fetched": fetched,
        }

        # DEBUG: PostgreSQL 저장 직전 페이로드 확인
        print("=" * 80)
        print(f"[PG SAVE] article_id={article_id}, account_id={account_id}")
        print(f"[PG SAVE] metadata={raw_payload['metadata']}")
        print(f"[PG SAVE] fetched keys={list(fetched.keys())}")
        print(f"[PG SAVE] status_code={fetched.get('status_code')}")
        print(f"[PG SAVE] content_type={fetched.get('content_type')}")
        print(f"[PG SAVE] final_url={fetched.get('final_url')}")
        print(f"[PG SAVE] extracted_title={fetched.get('extracted_title')}")
        print(f"[PG SAVE] text length={len(fetched.get('text') or '')}")
        print(f"[PG SAVE] text preview:")
        print((fetched.get("text") or "")[:1000])
        print(f"[PG SAVE] html length={len(fetched.get('html') or '')}")
        print("=" * 80)

        try:
            self.content_repository.save(
                article_id=article_id,
                account_id=account_id,
                link=request.link,
                raw=raw_payload,
            )
        except Exception as exc:
            logger.error(
                "PostgreSQL 본문 저장 실패 (article_id=%s). MySQL 메타데이터를 롤백합니다.",
                article_id,
                exc_info=True,
            )
            self._rollback_metadata(article_id)
            raise InterestArticleContentPersistError(
                "관심 기사 본문 저장에 실패했습니다."
            ) from exc

        return SaveInterestArticleResponse(
            id=article_id,
            title=request.title,
            source=request.source,
            link=request.link,
            published_at=request.published_at,
            content=fetched.get("text") or "",
        )

    def _rollback_metadata(self, article_id: int) -> None:
        try:
            self.article_repository.delete(article_id)
        except Exception:
            logger.critical(
                "메타데이터 롤백 실패 (article_id=%s). 수동 정리가 필요합니다.",
                article_id,
                exc_info=True,
            )
