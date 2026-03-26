from app.domains.market_video.domain.entity.video_comment import VideoComment
from app.domains.market_video.infrastructure.orm.video_comment_orm import VideoCommentORM


class VideoCommentMapper:
    @staticmethod
    def to_orm(entity: VideoComment) -> VideoCommentORM:
        return VideoCommentORM(
            comment_id=entity.comment_id,
            video_id=entity.video_id,
            author_name=entity.author_name,
            text=entity.text,
            published_at=entity.published_at,
            like_count=entity.like_count,
            created_at=entity.created_at,
        )

    @staticmethod
    def to_entity(orm: VideoCommentORM) -> VideoComment:
        return VideoComment(
            id=orm.id,
            comment_id=orm.comment_id,
            video_id=orm.video_id,
            author_name=orm.author_name,
            text=orm.text,
            published_at=orm.published_at,
            like_count=orm.like_count,
            created_at=orm.created_at,
        )
