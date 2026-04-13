from typing import Annotated, List, Literal, Optional, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """LangGraph 멀티 에이전트 그래프의 공통 실행 컨텍스트."""

    # 사용자 원본 입력
    input: str

    # 누적되는 메시지 메모리 (각 에이전트가 자기 발화를 append)
    messages: Annotated[List[BaseMessage], add_messages]

    # 노드별 산출물
    plan: Optional[str]
    research: Optional[str]
    analysis: Optional[str]

    # Reviewer 판정 + 무한 루프 방지용 카운터
    review: Optional[Literal["approved", "needs_revision"]]
    iteration: int

    # 그래프의 최종 산출물
    final_output: Optional[str]
