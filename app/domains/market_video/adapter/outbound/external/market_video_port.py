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


class MarketVideoPort(ABC):
    @abstractmethod
    def get_channel_videos(self, channel_id: str, published_after: str, max_results: int) -> list[ChannelVideoItem]:
        pass

    @abstractmethod
    def get_video_statistics(self, video_ids: list[str]) -> dict[str, int]:
        pass
