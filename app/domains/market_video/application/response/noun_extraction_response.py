from typing import List

from pydantic import BaseModel


class NounFrequency(BaseModel):
    noun: str
    count: int


class NounExtractionResponse(BaseModel):
    nouns: List[NounFrequency]
    total_nouns: int
    total_comments: int
