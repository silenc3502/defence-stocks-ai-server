from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ChannelVideoItem:
    video_id: str
    title: str
    thumbnail_url: str
    channel_name: str
    published_at: datetime
    video_url: str
    view_count: Optional[int] = None


@dataclass
class VideoCommentItem:
    comment_id: str
    author_name: str
    text: str
    published_at: datetime
    like_count: int


class MarketVideoPort(ABC):
    @abstractmethod
    def get_channel_videos(self, channel_id: str, published_after: str, max_results: int, query: str = "") -> list[ChannelVideoItem]:
        pass

    @abstractmethod
    def get_video_statistics(self, video_ids: list[str]) -> dict[str, int]:
        pass

    @abstractmethod
    def get_video_comments(self, video_id: str, max_results: int, order: str = "relevance") -> list[VideoCommentItem]:
        pass
