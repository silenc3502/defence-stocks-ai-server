"""LangGraph 노드에서 공통으로 사용하는 LLM 호출 헬퍼."""
from langchain_core.messages import HumanMessage, SystemMessage

from app.infrastructure.agent.exceptions import AgentInvocationError
from app.infrastructure.agent.llm import get_chat_llm


def invoke_llm(node_name: str, system_prompt: str, user_prompt: str) -> str:
    """노드 공통 LLM 호출. 입출력 print + 실패 시 AgentInvocationError 래핑."""
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
