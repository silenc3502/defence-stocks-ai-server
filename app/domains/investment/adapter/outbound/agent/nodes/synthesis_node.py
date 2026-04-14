"""Synthesis — 최종 응답 생성 + 면책 문구 부착."""
from typing import Any, Dict

from langchain_core.messages import AIMessage

from app.domains.investment.adapter.outbound.agent.llm_invoker import invoke_llm
from app.domains.investment.adapter.outbound.agent.state import InvestmentState

_DISCLAIMER = (
    "\n\n---\n"
    "⚠️ 본 응답은 투자 권유가 아닌 정보 제공 목적이며, "
    "투자 판단의 책임은 전적으로 투자자 본인에게 있습니다."
)


def synthesis_node(state: InvestmentState) -> Dict[str, Any]:
    print("\n" + "=" * 60)
    print(f"[Synthesis] 시작")
    print(f"[Synthesis] analysis_result 길이: {len(state.get('analysis_result') or '')}자")
    print("=" * 60)

    synthesis = invoke_llm(
        "Synthesis",
        system_prompt=(
            "당신은 투자 판단 참고 응답 생성 에이전트입니다. "
            "분석 결과를 사용자 질문에 맞게 종합하여 한국어로 응답하세요. "
            "면책 문구는 시스템이 자동 부착하므로 본문에 넣지 마세요."
        ),
        user_prompt=(
            f"사용자 질문:\n{state['input']}\n\n"
            f"분석 결과:\n{state.get('analysis_result') or '(없음)'}"
        ),
    )

    final = synthesis + _DISCLAIMER

    print(f"[Synthesis] 최종 응답 길이: {len(final)}자")
    print(f"[Synthesis] 응답 앞 300자:")
    print(final[:300])
    print("=" * 60)

    return {
        "final_output": final,
        "next_agent": "done",
        "messages": [AIMessage(content=synthesis, name="Synthesis")],
    }
