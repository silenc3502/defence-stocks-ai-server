"""뉴스 데이터 소스 — news 도메인의 CollectInvestmentNewsUseCase 재사용.

- 뉴스 검색(SERP) → 본문 fetch(httpx + trafilatura) → MySQL/PG 양쪽 저장
- keyword 가 None 이면 기본 방산 키워드로 fallback
- 결과를 텍스트로 포맷하여 Retrieval Agent 의 retrieval_data 에 적재
"""
from typing import Optional

from app.domains.news.adapter.outbound.external.httpx_article_content_fetcher import (
    HttpxArticleContentFetcher,
)
from app.domains.news.adapter.outbound.external.serp_news_search_client import (
    SerpNewsSearchClient,
)
from app.domains.news.adapter.outbound.persistence.investment_news_content_repository_impl import (
    InvestmentNewsContentRepositoryImpl,
)
from app.domains.news.adapter.outbound.persistence.investment_news_repository_impl import (
    InvestmentNewsRepositoryImpl,
)
from app.domains.news.application.usecase.collect_investment_news_usecase import (
    CollectInvestmentNewsUseCase,
)
from app.infrastructure.database.postgres_session import PostgresSessionLocal
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.external.serp.serp_api_client import serp_api_client

_FALLBACK_KEYWORD = "한국 방산주"
_MAX_RESULTS = 5
_CONTENT_PREVIEW_LEN = 500


def fetch_news(keyword: Optional[str] = None) -> str:
    query = keyword or _FALLBACK_KEYWORD
    if keyword:
        print(f"  [뉴스] 사용자 키워드 사용: {query!r}")
    else:
        print(f"  [뉴스] 키워드 없음 → 기본 쿼리 fallback: {query!r}")

    mysql_db = SessionLocal()
    pg_db = PostgresSessionLocal()
    try:
        usecase = CollectInvestmentNewsUseCase(
            news_search_port=SerpNewsSearchClient(serp_api_client),
            content_fetcher=HttpxArticleContentFetcher(),
            news_repository=InvestmentNewsRepositoryImpl(mysql_db),
            content_repository=InvestmentNewsContentRepositoryImpl(pg_db),
        )
        result = usecase.execute(
            keyword=query,
            max_results=_MAX_RESULTS,
            original_keyword=keyword,
        )
    finally:
        mysql_db.close()
        pg_db.close()

    return _format_for_retrieval(result, query)


def _format_for_retrieval(result, query_used: str) -> str:
    """Retrieval Agent 가 분석하기 좋은 텍스트 형태로 포맷."""
    if not result.items:
        return (
            f"(뉴스 본문 수집 결과 없음 — query={query_used}, "
            f"SERP 총 {result.total_searched}건, 실패 {result.failure_count}건)"
        )

    header = (
        f"[투자 뉴스 본문 수집: {result.success_count}건 성공 "
        f"(SERP 총 {result.total_searched}건 중, 실패 {result.failure_count}건) — "
        f"검색어: {query_used}]"
    )

    sections = [header]
    for i, item in enumerate(result.items):
        date_str = item.published_at.strftime("%Y-%m-%d") if item.published_at else "날짜 없음"
        block = [
            f"\n#{i + 1} [{date_str}] {item.title} ({item.source or '출처 미상'})",
            f"  link: {item.link}",
            f"  본문 요약 (앞 {_CONTENT_PREVIEW_LEN}자):",
            f"  {item.content[:_CONTENT_PREVIEW_LEN].strip()}",
        ]
        sections.append("\n".join(block))

    return "\n".join(sections)
