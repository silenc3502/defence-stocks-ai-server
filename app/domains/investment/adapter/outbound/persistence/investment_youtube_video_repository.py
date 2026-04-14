from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional


class InvestmentYoutubeVideoRepository(ABC):
    """Investment YouTube 영상 메타데이터 저장소 Port (MySQL)."""

    @abstractmethod
    def save(
        self,
        log_id: int,
        video_id: str,
        title: str,
        channel_name: Optional[str],
        video_url: str,
        thumbnail_url: Optional[str],
        published_at: Optional[datetime],
        comment_count: int,
    ) -> int:
        """
        :return: 저장된 video row id (cross-DB 키로 사용됨)
        """
        raise NotImplementedError
