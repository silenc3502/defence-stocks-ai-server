"""뉴스 데이터 소스 — SearchNewsUseCase 재사용.

keyword 가 None 인 경우(테마·섹터 질문) 기본 방산 키워드로 fallback.
"""
from typing import Optional

from app.domains.news.adapter.outbound.external.serp_news_search_client import (
    SerpNewsSearchClient,
)
from app.domains.news.application.usecase.search_news_usecase import SearchNewsUseCase
from app.infrastructure.external.serp.serp_api_client import serp_api_client

_FALLBACK_KEYWORD = "한국 방산주"


def fetch_news(keyword: Optional[str] = None) -> str:
    query = keyword or _FALLBACK_KEYWORD
    if keyword:
        print(f"  [뉴스] 사용자 키워드 사용: {query!r}")
    else:
        print(f"  [뉴스] 키워드 없음 → 기본 쿼리 fallback: {query!r}")

    usecase = SearchNewsUseCase(SerpNewsSearchClient(serp_api_client))
    result = usecase.execute(keyword=query, page=1, page_size=5)
    print(f"  [뉴스] 응답: total_count={result.total_count}, items={len(result.items)}건")

    if not result.items:
        print("  [뉴스] 결과 없음")
        return f"(뉴스 검색 결과 없음 — query={query})"

    lines = [f"[뉴스 검색 결과: {result.total_count}건 중 상위 {len(result.items)}건 (검색어: {query})]"]
    for i, item in enumerate(result.items):
        date_str = item.published_at.strftime("%Y-%m-%d") if item.published_at else "날짜 없음"
        lines.append(f"- [{date_str}] {item.title} ({item.source}) {item.link}")
        print(f"  [뉴스] #{i + 1} {date_str} | {item.source} | {item.title[:60]}")

    return "\n".join(lines)
