from datetime import datetime
from typing import Optional


class VideoComment:
    def __init__(
        self,
        comment_id: str,
        video_id: str,
        author_name: str,
        text: str,
        published_at: datetime,
        like_count: int,
        id: Optional[int] = None,
        created_at: Optional[datetime] = None,
    ):
        self.id = id
        self.comment_id = comment_id
        self.video_id = video_id
        self.author_name = author_name
        self.text = text
        self.published_at = published_at
        self.like_count = like_count
        self.created_at = created_at or datetime.now()
