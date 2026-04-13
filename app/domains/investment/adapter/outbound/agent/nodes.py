"""투자 판단 워크플로우 에이전트 노드 (흐름 구조만 — 세부 구현은 후속 백로그).

각 노드는 State 를 받아 자기 역할의 결과를 State 에 기록하고 반환한다.
Orchestrator 만 `next_agent` 를 결정하여 라우팅을 제어한다.
"""
import logging
from typing import Any, Dict

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.domains.investment.adapter.outbound.agent.state import InvestmentState
from app.infrastructure.agent.exceptions import AgentInvocationError
from app.infrastructure.agent.llm import get_chat_llm

logger = logging.getLogger(__name__)

_MAX_ITERATIONS = 3


# ------------------------------------------------------------------
# 공통 헬퍼
# ------------------------------------------------------------------
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
        raise AgentInvocationError(f"{node_name} LLM 호출 실패: {exc}") from exc

    text = response.content if isinstance(response.content, str) else str(response.content)
    logger.info("[%s] output: %s", node_name, text[:200].replace("\n", " "))
    return text


# ------------------------------------------------------------------
# Orchestrator — 다음 에이전트를 동적으로 결정
# ------------------------------------------------------------------
def orchestrator_node(state: InvestmentState) -> Dict[str, Any]:
    iteration = state.get("iteration", 0) + 1

    # 반복 제한 초과 → 강제 종료 또는 합성
    if iteration > _MAX_ITERATIONS:
        next_agent = "synthesis" if not state.get("final_output") else "done"
        logger.info("[Orchestrator] 반복 제한 도달 (iter=%s) → %s", iteration, next_agent)
        return {"next_agent": next_agent, "iteration": iteration}

    # LLM 에게 현재 상태 요약을 주고 다음 단계를 결정하게 함
    status_summary = (
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

    return {
        "next_agent": next_agent,
        "iteration": iteration,
        "messages": [AIMessage(content=f"[Orchestrator] next → {next_agent}", name="Orchestrator")],
    }


# ------------------------------------------------------------------
# Retrieval — 원천 데이터 수집 (stub: LLM 시뮬레이션)
# ------------------------------------------------------------------
def retrieval_node(state: InvestmentState) -> Dict[str, Any]:
    # TODO: 실제 구현 시 SERP 뉴스 검색, 저장된 관심 기사 조회 등으로 교체
    data = _invoke_llm(
        "Retrieval",
        system_prompt=(
            "당신은 투자 데이터 수집 에이전트입니다. "
            "사용자 질문과 관련된 최신 뉴스·종목 정보·시장 데이터를 "
            "검색한 것처럼 정리하세요. (현재는 stub 구현)"
        ),
        user_prompt=f"사용자 질문:\n{state['input']}",
    )
    return {
        "retrieval_data": data,
        "messages": [AIMessage(content=data, name="Retrieval")],
    }


# ------------------------------------------------------------------
# Analysis — 수집 데이터 분석 (stub)
# ------------------------------------------------------------------
def analysis_node(state: InvestmentState) -> Dict[str, Any]:
    # TODO: 실제 구현 시 정량 분석, 감성 분석, 리스크 평가 등으로 확장
    analysis = _invoke_llm(
        "Analysis",
        system_prompt=(
            "당신은 투자 분석 에이전트입니다. "
            "수집된 데이터를 바탕으로 종목 전망·리스크·투자 포인트를 분석하세요."
        ),
        user_prompt=(
            f"사용자 질문:\n{state['input']}\n\n"
            f"수집 데이터:\n{state.get('retrieval_data') or '(없음)'}"
        ),
    )
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
    return {
        "final_output": synthesis + _DISCLAIMER,
        "next_agent": "done",
        "messages": [AIMessage(content=synthesis, name="Synthesis")],
    }
