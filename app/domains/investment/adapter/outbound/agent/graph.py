"""투자 판단 Orchestrator 중심 LangGraph 워크플로우.

흐름:
    START → orchestrator ──┬─ "retrieval"  → retrieval  → orchestrator
                           ├─ "analysis"   → analysis   → orchestrator
                           ├─ "synthesis"  → synthesis   → orchestrator
                           └─ "done"       → END
"""
import logging
from functools import lru_cache
from typing import Any, Dict

from langgraph.graph import END, START, StateGraph

from app.domains.investment.adapter.outbound.agent.nodes import (
    analysis_node,
    orchestrator_node,
    retrieval_node,
    synthesis_node,
)
from app.domains.investment.adapter.outbound.agent.state import InvestmentState
from app.infrastructure.agent.exceptions import AgentInvocationError

logger = logging.getLogger(__name__)


def _route_from_orchestrator(state: InvestmentState) -> str:
    next_agent = state.get("next_agent") or "done"
    return next_agent if next_agent != "done" else "__end__"


def build_investment_graph():
    graph = StateGraph(InvestmentState)

    # 노드 등록
    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("retrieval", retrieval_node)
    graph.add_node("analysis", analysis_node)
    graph.add_node("synthesis", synthesis_node)

    # 엣지: START → orchestrator
    graph.add_edge(START, "orchestrator")

    # Orchestrator 조건부 분기
    graph.add_conditional_edges(
        "orchestrator",
        _route_from_orchestrator,
        {
            "retrieval": "retrieval",
            "analysis": "analysis",
            "synthesis": "synthesis",
            "__end__": END,
        },
    )

    # 각 Agent 실행 후 → orchestrator 로 복귀
    graph.add_edge("retrieval", "orchestrator")
    graph.add_edge("analysis", "orchestrator")
    graph.add_edge("synthesis", "orchestrator")

    return graph.compile()


@lru_cache(maxsize=1)
def _get_compiled_graph():
    return build_investment_graph()


def run_investment_workflow(user_input: str) -> Dict[str, Any]:
    """투자 판단 멀티 에이전트 워크플로우 단일 진입점.

    :param user_input: 사용자 투자 질문 텍스트
    :return: 최종 state dict (final_output 포함)
    :raises AgentInvocationError: 노드 LLM 호출 또는 그래프 실행 실패
    """
    initial_state: InvestmentState = {
        "input": user_input,
        "messages": [],
        "next_agent": None,
        "retrieval_data": None,
        "analysis_result": None,
        "final_output": None,
        "iteration": 0,
    }

    logger.info("[InvestmentWorkflow] 시작 input=%s", user_input[:200])
    try:
        result = _get_compiled_graph().invoke(initial_state)
    except AgentInvocationError:
        raise
    except Exception as exc:
        logger.error("[InvestmentWorkflow] 실행 실패: %s", exc, exc_info=True)
        raise AgentInvocationError(f"투자 판단 워크플로우 실행 실패: {exc}") from exc

    logger.info(
        "[InvestmentWorkflow] 완료 iter=%s final_output=%s",
        result.get("iteration"),
        (result.get("final_output") or "")[:200],
    )
    return result
