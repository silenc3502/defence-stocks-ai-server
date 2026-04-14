from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.infrastructure.database.session import Base


class InvestmentYoutubeVideoORM(Base):
    """Investment 워크플로우가 수집한 영상 메타데이터 (MySQL).

    이 테이블의 `id` 가 PostgreSQL investment_youtube_video_comments 의
    cross-DB 키로 사용된다.
    """

    __tablename__ = "investment_youtube_videos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    log_id = Column(Integer, ForeignKey("investment_youtube_logs.id"), nullable=False, index=True)
    video_id = Column(String(32), nullable=False, index=True)        # YouTube video_id
    title = Column(String(500), nullable=False)
    channel_name = Column(String(255), nullable=True)
    video_url = Column(String(500), nullable=False)
    thumbnail_url = Column(String(500), nullable=True)
    published_at = Column(DateTime, nullable=True)
    comment_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
