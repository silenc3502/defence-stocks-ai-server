from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ReadBoardResponse(BaseModel):
    board_id: Optional[int]
    title: str
    content: str
    nickname: str
    created_at: datetime
    updated_at: datetime
