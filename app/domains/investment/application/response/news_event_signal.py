from typing import List, Literal

from pydantic import BaseModel


class NewsEvent(BaseModel):
    event: str
    impact: Literal["high", "medium", "low"]


class NewsEventSignal(BaseModel):
    """뉴스 기반 투자 이벤트 신호."""

    positive_events: List[NewsEvent]
    negative_events: List[NewsEvent]
    keywords: List[str]
