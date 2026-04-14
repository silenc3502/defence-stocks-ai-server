"""Analysis — 기존 AskAnalysisUseCase + Retrieval 수집 데이터 보강 분석."""
from typing import Any, Dict

from langchain_core.messages import AIMessage

from app.domains.investment.adapter.outbound.agent.llm_invoker import invoke_llm
from app.domains.investment.adapter.outbound.agent.state import InvestmentState
from app.domains.investment.adapter.outbound.data_source.analysis_source import (
    run_ask_analysis,
)


def analysis_node(state: InvestmentState) -> Dict[str, Any]:
    parsed = state.get("parsed_query") or {}
    retrieval_data = state.get("retrieval_data") or ""

    print("\n" + "=" * 60)
    print(f"[Analysis] 시작")
    print(f"[Analysis] intent: {parsed.get('intent')}")
    print(f"[Analysis] retrieval_data 길이: {len(retrieval_data)}자")
    print("=" * 60)

    # 1단계: 기존 AskAnalysisUseCase 활용 (DB 의 댓글 키워드 + 종목 데이터 기반)
    print("[Analysis] AskAnalysisUseCase 호출 (댓글 키워드 + 종목 컨텍스트 기반)")
    base_analysis = run_ask_analysis(state["input"])
    print(f"[Analysis] AskAnalysisUseCase 결과 길이: {len(base_analysis)}자")
    print(f"[Analysis] 결과 앞 300자: {base_analysis[:300]}")

    # 2단계: Retrieval 수집 데이터를 추가 컨텍스트로 LLM 보강 분석
    print("[Analysis] Retrieval 수집 데이터 보강 분석 시작")
    combined_analysis = invoke_llm(
        "Analysis",
        system_prompt=(
            "당신은 투자 분석 에이전트입니다. "
            "아래 두 가지 소스를 종합하여 종목 전망·리스크·투자 포인트를 분석하세요:\n"
            "1. [기존 분석] 유튜브 댓글 키워드와 방산주 데이터 기반 분석 결과\n"
            "2. [수집 데이터] Retrieval Agent 가 수집한 최신 뉴스·영상·종목 데이터"
        ),
        user_prompt=(
            f"사용자 질문:\n{state['input']}\n"
            f"질문 의도: {parsed.get('intent')}\n\n"
            f"[기존 분석]\n{base_analysis}\n\n"
            f"[수집 데이터]\n{retrieval_data}"
        ),
    )

    print(f"[Analysis] 최종 분석 결과 길이: {len(combined_analysis)}자")
    print("=" * 60)

    return {
        "analysis_result": combined_analysis,
        "messages": [AIMessage(content=combined_analysis, name="Analysis")],
    }
