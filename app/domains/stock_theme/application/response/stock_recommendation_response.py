from typing import List

from pydantic import BaseModel


class MatchedStock(BaseModel):
    name: str
    code: str
    themes: List[str]
    matched_keywords: List[str]
    relevance_score: int


class MatchedTheme(BaseModel):
    theme: str
    matched_keywords: List[str]
    relevance_score: int


class StockRecommendationResponse(BaseModel):
    stocks: List[MatchedStock]
    themes: List[MatchedTheme]
    input_keywords_count: int
