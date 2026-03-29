from typing import List

from pydantic import BaseModel


class MatchedStock(BaseModel):
    name: str
    code: str
    themes: List[str]
    matched_keywords: List[str]
    relevance_score: int
    reason: str = ""


class StockRecommendationResponse(BaseModel):
    stocks: List[MatchedStock]
    input_keywords_count: int
