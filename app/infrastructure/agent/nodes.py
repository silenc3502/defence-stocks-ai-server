import logging
from typing import Any, Dict

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.infrastructure.agent.exceptions import AgentInvocationError
from app.infrastructure.agent.llm import get_chat_llm
from app.infrastructure.agent.state import AgentState

logger = logging.getLogger(__name__)

_MAX_ITERATIONS = 2  # Researcher → ... → Reviewer 루프 최대 횟수


def _invoke_llm(node_name: str, system_prompt: str, user_prompt: str) -> str:
    logger.info("[%s] input: %s", node_name, user_prompt[:200].replace("\n", " "))
    try:
        response = get_chat_llm().invoke(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ]
        )
    except Exception as exc:
        logger.error("[%s] LLM 호출 실패: %s", node_name, exc, exc_info=True)
        raise AgentInvocationError(
            f"{node_name} 에이전트 LLM 호출 실패: {exc}"
        ) from exc

    content = response.content
    text = content if isinstance(content, str) else str(content)
    logger.info("[%s] output: %s", node_name, text[:200].replace("\n", " "))
    return text


def planner_node(state: AgentState) -> Dict[str, Any]:
    plan = _invoke_llm(
        "Planner",
        system_prompt=(
            "당신은 멀티 에이전트 워크플로우의 Planner 입니다. "
            "사용자 요청을 받아 후속 에이전트(Researcher → Analyst)가 수행할 "
            "단계별 계획을 한국어로 5줄 이내로 작성하세요. 각 줄은 '- ' 로 시작합니다."
        ),
        user_prompt=f"사용자 요청:\n{state['input']}",
    )
    return {
        "plan": plan,
        "messages": [AIMessage(content=plan, name="Planner")],
    }


def researcher_node(state: AgentState) -> Dict[str, Any]:
    research = _invoke_llm(
        "Researcher",
        system_prompt=(
            "당신은 Researcher 입니다. Planner 의 계획을 참고하여 "
            "주제와 관련된 핵심 사실/배경/데이터 포인트를 한국어로 정리하세요. "
            "출처가 불확실하면 '확인 필요' 라고 명시하세요."
        ),
        user_prompt=(
            f"계획:\n{state.get('plan') or '(계획 없음)'}\n\n"
            f"원본 요청:\n{state['input']}"
        ),
    )
    return {
        "research": research,
        "messages": [AIMessage(content=research, name="Researcher")],
    }


def analyst_node(state: AgentState) -> Dict[str, Any]:
    analysis = _invoke_llm(
        "Analyst",
        system_prompt=(
            "당신은 Analyst 입니다. Researcher 의 자료를 바탕으로 "
            "사용자 요청에 대한 분석/인사이트/결론을 한국어로 작성하세요. "
            "추측은 명시적으로 표시하세요."
        ),
        user_prompt=(
            f"원본 요청:\n{state['input']}\n\n"
            f"리서치 자료:\n{state.get('research') or '(자료 없음)'}"
        ),
    )
    return {
        "analysis": analysis,
        "messages": [AIMessage(content=analysis, name="Analyst")],
    }


def reviewer_node(state: AgentState) -> Dict[str, Any]:
    iteration = state.get("iteration", 0) + 1

    verdict_text = _invoke_llm(
        "Reviewer",
        system_prompt=(
            "당신은 Reviewer 입니다. Analyst 의 결과물을 검토하여 "
            "정확성/완성도/사용자 요청 충족 여부를 평가하세요. "
            "응답은 다음 두 가지 형식 중 하나만 사용하세요:\n"
            "- approved: <짧은 사유>\n"
            "- needs_revision: <개선 요청 사항>\n"
            "확신이 안 서면 approved 를 고르세요."
        ),
        user_prompt=(
            f"원본 요청:\n{state['input']}\n\n"
            f"분석 결과:\n{state.get('analysis') or '(분석 없음)'}"
        ),
    )

    raw = verdict_text.strip().lower()
    if raw.startswith("approved"):
        verdict = "approved"
    elif raw.startswith("needs_revision") and iteration < _MAX_ITERATIONS:
        verdict = "needs_revision"
    else:
        # 무한 루프 방지: 최대 반복 횟수 도달 시 강제 승인
        verdict = "approved"

    return {
        "review": verdict,
        "iteration": iteration,
        "messages": [AIMessage(content=verdict_text, name="Reviewer")],
        "final_output": state.get("analysis") if verdict == "approved" else None,
    }
