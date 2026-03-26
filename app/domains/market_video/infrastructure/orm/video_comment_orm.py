from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime

from app.infrastructure.database.session import Base


class VideoCommentORM(Base):
    __tablename__ = "video_comments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    comment_id = Column(String(128), unique=True, nullable=False, index=True)
    video_id = Column(String(64), nullable=False, index=True)
    author_name = Column(String(255), nullable=False)
    text = Column(Text, nullable=False)
    published_at = Column(DateTime, nullable=False)
    like_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
