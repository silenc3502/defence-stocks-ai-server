from typing import Optional

from sqlalchemy.orm import Session

from app.domains.market_video.adapter.outbound.persistence.video_comment_repository import VideoCommentRepository
from app.domains.market_video.domain.entity.video_comment import VideoComment
from app.domains.market_video.infrastructure.mapper.video_comment_mapper import VideoCommentMapper
from app.domains.market_video.infrastructure.orm.video_comment_orm import VideoCommentORM


class VideoCommentRepositoryImpl(VideoCommentRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(self, entity: VideoComment) -> VideoComment:
        orm = VideoCommentMapper.to_orm(entity)
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return VideoCommentMapper.to_entity(orm)

    def find_by_comment_id(self, comment_id: str) -> Optional[VideoComment]:
        orm = self.db.query(VideoCommentORM).filter(VideoCommentORM.comment_id == comment_id).first()
        if orm is None:
            return None
        return VideoCommentMapper.to_entity(orm)

    def delete_by_video_id(self, video_id: str) -> None:
        self.db.query(VideoCommentORM).filter(VideoCommentORM.video_id == video_id).delete()
        self.db.commit()

    def find_by_video_id(self, video_id: str) -> list[VideoComment]:
        orms = (
            self.db.query(VideoCommentORM)
            .filter(VideoCommentORM.video_id == video_id)
            .order_by(VideoCommentORM.like_count.desc())
            .all()
        )
        return [VideoCommentMapper.to_entity(orm) for orm in orms]
