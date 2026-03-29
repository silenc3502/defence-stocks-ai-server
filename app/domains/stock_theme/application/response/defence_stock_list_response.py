from typing import List

from pydantic import BaseModel


class DefenceStockItem(BaseModel):
    name: str
    code: str
    themes: List[str]


class DefenceStockListResponse(BaseModel):
    stocks: List[DefenceStockItem]
    total_count: int
