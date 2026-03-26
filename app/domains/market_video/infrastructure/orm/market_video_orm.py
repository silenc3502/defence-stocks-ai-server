from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime

from app.infrastructure.database.session import Base


class MarketVideoORM(Base):
    __tablename__ = "market_videos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(String(64), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    channel_name = Column(String(255), nullable=False)
    published_at = Column(DateTime, nullable=False)
    view_count = Column(Integer, nullable=False, default=0)
    thumbnail_url = Column(Text, nullable=False)
    video_url = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
