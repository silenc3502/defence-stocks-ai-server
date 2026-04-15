from typing import List, Literal

from pydantic import BaseModel


class DecisionReasons(BaseModel):
    positive: List[str]
    negative: List[str]


class InvestmentDecision(BaseModel):
    """수집 신호 기반 투자 판단 결과.

    direction/confidence/verdict 는 deterministic rule 로 산출된다.
    rationale 는 LLM 이 생성하는 서술형 설명이며 판단 자체에는 영향을 주지 않는다.
    """

    direction: Literal["bullish", "bearish", "neutral"]
    confidence: float                     # 0.0 ~ 1.0
    verdict: Literal["buy", "hold", "sell"]
    reasons: DecisionReasons
    risk_factors: List[str]
    rationale: str                        # LLM 이 생성한 판단 설명
