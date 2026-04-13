"""투자 판단 워크플로우 에이전트 노드.

Orchestrator 는 첫 호출 시 Query Parser 로 질문을 구조화하고,
이후 상태 기반으로 다음 에이전트를 동적으로 결정한다.
"""
import logging
from typing import Any, Dict

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.domains.investment.adapter.outbound.agent.query_parser import (
    parse_investment_query,
)
from app.domains.investment.adapter.outbound.agent.state import InvestmentState
from app.infrastructure.agent.exceptions import AgentInvocationError
from app.infrastructure.agent.llm import get_chat_llm

logger = logging.getLogger(__name__)

_MAX_ITERATIONS = 3


# ------------------------------------------------------------------
# 공통 헬퍼
# ------------------------------------------------------------------
def _invoke_llm(node_name: str, system_prompt: str, user_prompt: str) -> str:
    print(f"\n{'─' * 60}")
    print(f"[{node_name}] LLM 호출 시작")
    print(f"[{node_name}] prompt (앞 300자): {user_prompt[:300]}")
    print(f"{'─' * 60}")

    try:
        response = get_chat_llm().invoke(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ]
        )
    except Exception as exc:
        print(f"[{node_name}] ❌ LLM 호출 실패: {exc}")
        raise AgentInvocationError(f"{node_name} LLM 호출 실패: {exc}") from exc

    text = response.content if isinstance(response.content, str) else str(response.content)
    print(f"[{node_name}] LLM 응답 (앞 500자):")
    print(text[:500])
    print(f"{'─' * 60}")
    return text


# ------------------------------------------------------------------
# Orchestrator — Query Parser 호출 + 다음 에이전트 동적 결정
# ------------------------------------------------------------------
def orchestrator_node(state: InvestmentState) -> Dict[str, Any]:
    iteration = state.get("iteration", 0) + 1

    print("\n" + "=" * 60)
    print(f"[Orchestrator] ── iteration {iteration} 시작 ──")
    print(f"[Orchestrator] input: {state['input'][:100]}")
    print(f"[Orchestrator] parsed_query: {state.get('parsed_query')}")
    print(f"[Orchestrator] retrieval_data: {'있음' if state.get('retrieval_data') else '없음'}")
    print(f"[Orchestrator] analysis_result: {'있음' if state.get('analysis_result') else '없음'}")
    print(f"[Orchestrator] final_output: {'있음' if state.get('final_output') else '없음'}")
    print("=" * 60)

    updates: Dict[str, Any] = {"iteration": iteration}

    # 첫 호출: Query Parser 로 질문 구조화
    if state.get("parsed_query") is None:
        print("[Orchestrator] parsed_query 없음 → Query Parser 호출")
        parsed = parse_investment_query(state["input"])
        updates["parsed_query"] = parsed
    else:
        parsed = state["parsed_query"]

    # 반복 제한 초과
    if iteration > _MAX_ITERATIONS:
        next_agent = "synthesis" if not state.get("final_output") else "done"
        print(f"[Orchestrator] 반복 제한 도달 (iter={iteration}) → 강제 {next_agent}")
        updates["next_agent"] = next_agent
        return updates

    # 상태 기반 다음 에이전트 결정 (LLM 호출)
    status_summary = (
        f"parsed_query: {parsed}\n"
        f"retrieval_data: {'있음' if state.get('retrieval_data') else '없음'}\n"
        f"analysis_result: {'있음' if state.get('analysis_result') else '없음'}\n"
        f"final_output: {'있음' if state.get('final_output') else '없음'}\n"
        f"iteration: {iteration}"
    )

    decision = _invoke_llm(
        "Orchestrator",
        system_prompt=(
            "당신은 투자 판단 멀티 에이전트 워크플로우의 Orchestrator 입니다.\n"
            "현재 상태를 보고 다음에 실행할 에이전트를 하나만 선택하세요.\n"
            "선택지: retrieval, analysis, synthesis, done\n"
            "규칙:\n"
            "- 데이터가 없으면 → retrieval\n"
            "- 데이터는 있지만 분석이 없으면 → analysis\n"
            "- 분석까지 완료되었으면 → synthesis\n"
            "- 최종 응답이 완성되었으면 → done\n"
            "응답은 선택지 단어 하나만 출력하세요."
        ),
        user_prompt=f"사용자 질문:\n{state['input']}\n\n현재 상태:\n{status_summary}",
    )

    raw = decision.strip().lower()
    valid = {"retrieval", "analysis", "synthesis", "done"}
    next_agent = raw if raw in valid else "retrieval"

    print(f"[Orchestrator] 결정: next_agent = {next_agent}")
    print("=" * 60)

    updates["next_agent"] = next_agent
    updates["messages"] = [AIMessage(
        content=f"[Orchestrator] parsed={parsed}, next → {next_agent}",
        name="Orchestrator",
    )]
    return updates


# ------------------------------------------------------------------
# Retrieval — 원천 데이터 수집 (stub: LLM 시뮬레이션)
# ------------------------------------------------------------------
def retrieval_node(state: InvestmentState) -> Dict[str, Any]:
    parsed = state.get("parsed_query") or {}

    print("\n" + "=" * 60)
    print(f"[Retrieval] 시작")
    print(f"[Retrieval] company: {parsed.get('company')}")
    print(f"[Retrieval] required_data: {parsed.get('required_data')}")
    print("=" * 60)

    # TODO: 실제 구현 시 SERP 뉴스 검색, 저장된 관심 기사 조회 등으로 교체
    data = _invoke_llm(
        "Retrieval",
        system_prompt=(
            "당신은 투자 데이터 수집 에이전트입니다. "
            "사용자 질문과 파싱 정보를 참고하여 관련 뉴스·종목 정보·시장 데이터를 "
            "검색한 것처럼 정리하세요. (현재는 stub 구현)"
        ),
        user_prompt=(
            f"사용자 질문:\n{state['input']}\n\n"
            f"파싱 정보:\n{parsed}\n\n"
            f"필요 데이터: {parsed.get('required_data', [])}"
        ),
    )

    print(f"[Retrieval] 수집 데이터 길이: {len(data)}자")
    print("=" * 60)

    return {
        "retrieval_data": data,
        "messages": [AIMessage(content=data, name="Retrieval")],
    }


# ------------------------------------------------------------------
# Analysis — 수집 데이터 분석 (stub)
# ------------------------------------------------------------------
def analysis_node(state: InvestmentState) -> Dict[str, Any]:
    parsed = state.get("parsed_query") or {}

    print("\n" + "=" * 60)
    print(f"[Analysis] 시작")
    print(f"[Analysis] intent: {parsed.get('intent')}")
    print(f"[Analysis] retrieval_data 길이: {len(state.get('retrieval_data') or '')}자")
    print("=" * 60)

    # TODO: 실제 구현 시 정량 분석, 감성 분석, 리스크 평가 등으로 확장
    analysis = _invoke_llm(
        "Analysis",
        system_prompt=(
            "당신은 투자 분석 에이전트입니다. "
            "수집된 데이터를 바탕으로 종목 전망·리스크·투자 포인트를 분석하세요."
        ),
        user_prompt=(
            f"사용자 질문:\n{state['input']}\n\n"
            f"질문 의도: {parsed.get('intent')}\n\n"
            f"수집 데이터:\n{state.get('retrieval_data') or '(없음)'}"
        ),
    )

    print(f"[Analysis] 분석 결과 길이: {len(analysis)}자")
    print("=" * 60)

    return {
        "analysis_result": analysis,
        "messages": [AIMessage(content=analysis, name="Analysis")],
    }


# ------------------------------------------------------------------
# Synthesis — 최종 응답 생성 (stub, 면책 문구 포함)
# ------------------------------------------------------------------
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

    synthesis = _invoke_llm(
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
