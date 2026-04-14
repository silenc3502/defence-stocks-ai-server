"""Retrieval — required_data 기반 데이터 소스 라우팅."""
import logging
from typing import Any, Dict

from langchain_core.messages import AIMessage

from app.domains.investment.adapter.outbound.agent.state import InvestmentState
from app.domains.investment.adapter.outbound.data_source.source_registry import (
    SOURCE_REGISTRY,
)

logger = logging.getLogger(__name__)


def retrieval_node(state: InvestmentState) -> Dict[str, Any]:
    parsed = state.get("parsed_query") or {}
    required_data = parsed.get("required_data", [])
    # company 가 없으면 None 을 그대로 handler 에 전달 → handler 가 자체 fallback 사용
    keyword = parsed.get("company")

    print("\n" + "=" * 60)
    print(f"[Retrieval] 시작")
    print(f"[Retrieval] keyword: {keyword!r} ({'company 있음' if keyword else 'company 없음 → 각 소스 fallback'})")
    print(f"[Retrieval] required_data: {required_data}")
    print("=" * 60)

    sections: list[str] = []

    for source_key in required_data:
        handler = SOURCE_REGISTRY.get(source_key)

        if handler is None:
            print(f"[Retrieval] '{source_key}' → 미구현 소스, 건너뜀")
            sections.append(f"[{source_key}] (미구현 — 향후 확장 예정)")
            continue

        print(f"[Retrieval] '{source_key}' → 호출 시작")
        try:
            result_text = handler(keyword)
            print(f"[Retrieval] '{source_key}' → 성공 ({len(result_text)}자)")
            sections.append(result_text)
        except Exception as exc:
            print(f"[Retrieval] '{source_key}' → 실패: {exc}")
            logger.error("[Retrieval] %s 호출 실패: %s", source_key, exc, exc_info=True)
            sections.append(f"[{source_key}] (수집 실패: {exc})")

    data = "\n\n".join(sections) if sections else "(수집된 데이터 없음)"

    print(f"\n[Retrieval] 최종 retrieval_data 길이: {len(data)}자")
    print(f"[Retrieval] 호출된 소스: {[s for s in required_data if s in SOURCE_REGISTRY]}")
    print(f"[Retrieval] 건너뛴 소스: {[s for s in required_data if s not in SOURCE_REGISTRY]}")
    print("=" * 60)

    return {
        "retrieval_data": data,
        "messages": [AIMessage(content=data, name="Retrieval")],
    }
