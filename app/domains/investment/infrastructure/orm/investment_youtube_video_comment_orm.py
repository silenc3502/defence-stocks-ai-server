from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import JSONB

from app.infrastructure.database.postgres_session import PostgresBase


class InvestmentYoutubeVideoCommentORM(PostgresBase):
    """영상별 댓글 JSONB 저장소 (PostgreSQL).

    `id` 는 MySQL `investment_youtube_videos.id` 와 동일한 값을 가진다.
    (교차 DB FK 는 불가능하므로 애플리케이션 레벨에서 정합성 보장)
    """

    __tablename__ = "investment_youtube_video_comments"

    id = Column(Integer, primary_key=True, autoincrement=False)
    video_id = Column(String(32), nullable=False, index=True)   # YouTube video_id (조회 편의)
    comments = Column(JSONB, nullable=False)                     # [{comment_id, author, text, ...}]
    created_at = Column(DateTime, nullable=False, default=datetime.now)
