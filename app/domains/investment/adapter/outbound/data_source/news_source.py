"""뉴스 데이터 소스 — news 도메인의 CollectInvestmentNewsUseCase 재사용.

- 뉴스 검색(SERP) → 본문 fetch(httpx + trafilatura) → MySQL/PG 양쪽 저장
- keyword 가 None 이면 기본 방산 키워드로 fallback
- 결과를 텍스트로 포맷하여 Retrieval Agent 의 retrieval_data 에 적재
"""
from typing import Any, Dict, Optional, Tuple

from app.domains.investment.adapter.outbound.signal.news_signal_builder import (
    NewsSignalBuilder,
)
from app.domains.investment.application.usecase.analyze_news_events_usecase import (
    AnalyzeNewsEventsUseCase,
)
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


def fetch_news(keyword: Optional[str] = None) -> Tuple[str, Optional[Dict[str, Any]]]:
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

    # 뉴스 이벤트 신호 산출
    event_signal = _build_event_signal(result)

    text = _format_for_retrieval(result, query, event_signal)
    # 신호 payload 를 함께 반환 (State 에 저장되어 Analyzer 가 소비)
    has_events = bool(event_signal.positive_events or event_signal.negative_events)
    signal_payload = event_signal.model_dump() if has_events else None
    return text, signal_payload


def _build_event_signal(result):
    """수집된 뉴스로부터 NewsEventSignal 산출. 실패 시 빈 신호."""
    news_items = [
        {
            "title": item.title,
            "content": item.content,
            "source": item.source,
            "link": item.link,
        }
        for item in result.items
    ]
    try:
        usecase = AnalyzeNewsEventsUseCase(signal_builder=NewsSignalBuilder())
        signal = usecase.execute(news_items)
    except Exception as exc:
        print(f"  [뉴스] ❌ 이벤트 신호 산출 실패 (continue): {exc}")
        from app.domains.investment.application.response.news_event_signal import (
            NewsEventSignal,
        )
        signal = NewsEventSignal(positive_events=[], negative_events=[], keywords=[])

    _print_news_signal(signal)
    return signal


def _print_news_signal(signal) -> None:
    """NewsEventSignal 전체 지표를 pretty-print 로 출력."""
    print()
    print("  " + "┌" + "─" * 58 + "┐")
    print(f"  │ [NewsEventSignal]                                        │")
    print("  " + "├" + "─" * 58 + "┤")
    print(f"  │ positive_events ({len(signal.positive_events)}):")
    for e in signal.positive_events:
        print(f"  │   + [{e.impact:^6s}] {e.event}")
    print(f"  │ negative_events ({len(signal.negative_events)}):")
    for e in signal.negative_events:
        print(f"  │   - [{e.impact:^6s}] {e.event}")
    print(f"  │ keywords ({len(signal.keywords)}):")
    for kw in signal.keywords:
        print(f"  │   • {kw}")
    print("  " + "└" + "─" * 58 + "┘")
    print()


def _format_for_retrieval(result, query_used: str, event_signal) -> str:
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

    # 이벤트 신호 포맷
    sections.append(_format_event_signal(event_signal))

    return "\n".join(sections)


def _format_event_signal(signal) -> str:
    lines = ["\n[뉴스 이벤트 신호]"]
    if signal.positive_events:
        lines.append("- 긍정 이벤트:")
        for e in signal.positive_events:
            lines.append(f"  + [{e.impact}] {e.event}")
    if signal.negative_events:
        lines.append("- 부정 이벤트:")
        for e in signal.negative_events:
            lines.append(f"  - [{e.impact}] {e.event}")
    if signal.keywords:
        lines.append(f"- 핵심 키워드: {', '.join(signal.keywords[:15])}")
    if not (signal.positive_events or signal.negative_events or signal.keywords):
        lines.append("(추출된 이벤트 없음)")
    return "\n".join(lines)
