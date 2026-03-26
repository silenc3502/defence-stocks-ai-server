from datetime import datetime
from typing import List

from pydantic import BaseModel


class CommentItem(BaseModel):
    comment_id: str
    author_name: str
    text: str
    published_at: datetime
    like_count: int


class VideoComments(BaseModel):
    video_id: str
    title: str
    comments: List[CommentItem]
    comment_count: int


class CollectCommentsResponse(BaseModel):
    videos: List[VideoComments]
    total_videos: int
    total_comments: int
