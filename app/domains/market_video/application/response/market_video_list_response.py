from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class MarketVideoItem(BaseModel):
    video_id: str
    title: str
    thumbnail_url: str
    channel_name: str
    published_at: datetime
    video_url: str
    view_count: Optional[int] = None


class MarketVideoListResponse(BaseModel):
    items: List[MarketVideoItem]
    total_count: int
