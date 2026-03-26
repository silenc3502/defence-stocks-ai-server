from datetime import datetime
from typing import Optional


class MarketVideo:
    def __init__(
        self,
        video_id: str,
        title: str,
        channel_name: str,
        published_at: datetime,
        view_count: int,
        thumbnail_url: str,
        video_url: str,
        id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.video_id = video_id
        self.title = title
        self.channel_name = channel_name
        self.published_at = published_at
        self.view_count = view_count
        self.thumbnail_url = thumbnail_url
        self.video_url = video_url
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
