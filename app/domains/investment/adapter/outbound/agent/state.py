from typing import Annotated, List, Literal, Optional, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

NextAgent = Literal["retrieval", "analysis", "synthesis", "done"]


class InvestmentState(TypedDict):
    """투자 판단 멀티 에이전트 워크플로우 공유 State."""

    # 사용자 원본 질의
    input: str

    # 누적 메시지 메모리
    messages: Annotated[List[BaseMessage], add_messages]

    # Orchestrator 가 결정한 다음 에이전트 (라우팅 키)
    next_agent: Optional[NextAgent]

    # Retrieval Agent 수집 데이터
    retrieval_data: Optional[str]

    # Analysis Agent 분석 결과
    analysis_result: Optional[str]

    # Synthesis Agent 최종 응답
    final_output: Optional[str]

    # 반복 횟수 (무한 루프 방지)
    iteration: int
