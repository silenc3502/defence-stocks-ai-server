from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class BoardItem(BaseModel):
    board_id: Optional[int]
    title: str
    content: str
    account_id: int
    created_at: datetime
    updated_at: datetime


class BoardListResponse(BaseModel):
    items: List[BoardItem]
    current_page: int
    total_pages: int
    total_count: int
