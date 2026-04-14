"""Orchestrator — Query Parser 호출 + 다음 에이전트 동적 결정."""
from typing import Any, Dict

from langchain_core.messages import AIMessage

from app.domains.investment.adapter.outbound.agent.llm_invoker import invoke_llm
from app.domains.investment.adapter.outbound.agent.query_parser import (
    parse_investment_query,
)
from app.domains.investment.adapter.outbound.agent.state import InvestmentState

_MAX_ITERATIONS = 3


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

    # 상태 기반 다음 에이전트 결정 (LLM)
    status_summary = (
        f"parsed_query: {parsed}\n"
        f"retrieval_data: {'있음' if state.get('retrieval_data') else '없음'}\n"
        f"analysis_result: {'있음' if state.get('analysis_result') else '없음'}\n"
        f"final_output: {'있음' if state.get('final_output') else '없음'}\n"
        f"iteration: {iteration}"
    )

    decision = invoke_llm(
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
