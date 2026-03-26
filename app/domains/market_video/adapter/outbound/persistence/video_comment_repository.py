from abc import ABC, abstractmethod

from app.domains.market_video.domain.entity.video_comment import VideoComment


class VideoCommentRepository(ABC):
    @abstractmethod
    def save(self, entity: VideoComment) -> VideoComment:
        pass

    @abstractmethod
    def find_by_comment_id(self, comment_id: str) -> VideoComment | None:
        pass

    @abstractmethod
    def delete_by_video_id(self, video_id: str) -> None:
        pass

    @abstractmethod
    def find_by_video_id(self, video_id: str) -> list[VideoComment]:
        pass
