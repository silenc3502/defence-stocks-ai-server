from abc import ABC, abstractmethod
from typing import Any, List, Optional


class InvestmentYoutubeLogRepository(ABC):
    """Investment YouTube 수집 세션 헤더 저장소 Port (MySQL)."""

    @abstractmethod
    def save(
        self,
        keyword: Optional[str],
        query_used: str,
        video_count: int,
        comment_count: int,
        keyword_count: int,
        keywords_top: List[dict],
    ) -> int:
        """
        :return: 저장된 log id
        """
        raise NotImplementedError
