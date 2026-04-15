from typing import Annotated, List, Literal, Optional, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

NextAgent = Literal["retrieval", "analysis", "synthesis", "done"]


class ParsedQuery(TypedDict):
    """Query Parser 의 구조화된 파싱 결과."""

    company: Optional[str]       # 종목명/티커 (없으면 None)
    intent: str                  # "매수_판단" | "리스크_분석" | "전망_조회" | "비교_분석" | "일반_질의"
    required_data: List[str]     # ["뉴스", "재무", "시장_데이터", "업종_동향"] 등


class InvestmentState(TypedDict):
    """투자 판단 멀티 에이전트 워크플로우 공유 State."""

    # 사용자 원본 질의
    input: str

    # 누적 메시지 메모리
    messages: Annotated[List[BaseMessage], add_messages]

    # Query Parser 결과
    parsed_query: Optional[ParsedQuery]

    # Orchestrator 가 결정한 다음 에이전트 (라우팅 키)
    next_agent: Optional[NextAgent]

    # Retrieval Agent 수집 데이터 (텍스트 요약)
    retrieval_data: Optional[str]

    # Retrieval 단계에서 산출된 구조화된 신호 (Analyzer 가 소비)
    youtube_signal: Optional[dict]    # YoutubeSentimentSignal.model_dump()
    news_signal: Optional[dict]       # NewsEventSignal.model_dump()

    # Analysis Agent 분석 결과
    analysis_result: Optional[str]

    # Deterministic 투자 판단 (InvestmentDecision.model_dump())
    investment_decision: Optional[dict]

    # Synthesis Agent 최종 응답
    final_output: Optional[str]

    # 반복 횟수 (무한 루프 방지)
    iteration: int
