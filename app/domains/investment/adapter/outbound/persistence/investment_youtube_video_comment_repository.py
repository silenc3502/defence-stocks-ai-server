from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class InvestmentYoutubeVideoCommentRepository(ABC):
    """영상별 댓글 JSONB 저장소 Port (PostgreSQL).

    id 는 MySQL investment_youtube_videos.id 와 동일한 값을 사용한다.
    """

    @abstractmethod
    def save(
        self,
        video_pk: int,
        video_id: str,
        comments: List[Dict[str, Any]],
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def find_by_video_pk(self, video_pk: int) -> Optional[List[Dict[str, Any]]]:
        """MySQL 영상 PK 로 댓글 목록을 조회한다."""
        raise NotImplementedError
