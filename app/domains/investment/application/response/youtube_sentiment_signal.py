from typing import List

from pydantic import BaseModel


class SentimentDistribution(BaseModel):
    positive: float
    neutral: float
    negative: float


class YoutubeSentimentSignal(BaseModel):
    """유튜브 댓글 기반 투자 심리 신호."""

    sentiment_distribution: SentimentDistribution
    sentiment_score: float           # -1.0 (완전 부정) ~ +1.0 (완전 긍정)
    bullish_keywords: List[str]      # 긍정 댓글에서 추출한 상위 키워드
    bearish_keywords: List[str]      # 부정 댓글에서 추출한 상위 키워드
    topics: List[str]                # 전체 댓글 기준 상위 키워드
    volume: int                      # 분석에 사용된 댓글 수
