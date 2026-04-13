import logging
from functools import lru_cache
from typing import Any, Dict

from langgraph.graph import END, START, StateGraph

from app.infrastructure.agent.exceptions import AgentInvocationError
from app.infrastructure.agent.nodes import (
    analyst_node,
    planner_node,
    researcher_node,
    reviewer_node,
)
from app.infrastructure.agent.state import AgentState

logger = logging.getLogger(__name__)


def _route_after_review(state: AgentState) -> str:
    """Reviewer 결과에 따른 조건부 라우팅."""
    if state.get("review") == "needs_revision":
        return "researcher"
    return "__end__"


def build_agent_graph():
    """LangGraph 멀티 에이전트 그래프 구성 + 컴파일.

    흐름:
        START → planner → researcher → analyst → reviewer
                                           ↑          │
                                           └──── needs_revision
                                                      │
                                                    approved → END
    """
    graph = StateGraph(AgentState)

    graph.add_node("planner", planner_node)
    graph.add_node("researcher", researcher_node)
    graph.add_node("analyst", analyst_node)
    graph.add_node("reviewer", reviewer_node)

    graph.add_edge(START, "planner")
    graph.add_edge("planner", "researcher")
    graph.add_edge("researcher", "analyst")
    graph.add_edge("analyst", "reviewer")
    graph.add_conditional_edges(
        "reviewer",
        _route_after_review,
        {
            "researcher": "researcher",
            "__end__": END,
        },
    )

    return graph.compile()


@lru_cache(maxsize=1)
def _get_compiled_graph():
    return build_agent_graph()


def run_agent_workflow(user_input: str) -> Dict[str, Any]:
    """멀티 에이전트 그래프 단일 진입점.

    :param user_input: 사용자 원본 요청 텍스트
    :return: 최종 state dict (`final_output`, `plan`, `research`, `analysis`,
             `review`, `iteration`, `messages` 포함)
    :raises AgentInvocationError: 노드 LLM 호출 실패 또는 그래프 실행 실패
    """
    initial_state: AgentState = {
        "input": user_input,
        "messages": [],
        "plan": None,
        "research": None,
        "analysis": None,
        "review": None,
        "iteration": 0,
        "final_output": None,
    }

    logger.info("[Workflow] 시작 input=%s", user_input[:200])
    try:
        result = _get_compiled_graph().invoke(initial_state)
    except AgentInvocationError:
        raise
    except Exception as exc:
        logger.error("[Workflow] 그래프 실행 실패: %s", exc, exc_info=True)
        raise AgentInvocationError(f"그래프 실행 실패: {exc}") from exc

    logger.info(
        "[Workflow] 완료 iter=%s review=%s final_output=%s",
        result.get("iteration"),
        result.get("review"),
        (result.get("final_output") or "")[:200],
    )
    return result
