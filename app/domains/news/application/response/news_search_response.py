from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class NewsItem(BaseModel):
    title: str
    source: Optional[str] = None
    link: str
    published_at: Optional[datetime] = None


class NewsSearchResponse(BaseModel):
    items: List[NewsItem]
    current_page: int
    page_size: int
    total_count: int
