from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Integer, String

from app.infrastructure.database.session import Base


class InvestmentYoutubeLogORM(Base):
    """Investment 워크플로우의 YouTube 수집 세션 헤더 (MySQL).

    한 번의 fetch_youtube 호출 = 1 row.
    영상 메타데이터는 investment_youtube_videos 테이블로 분리.
    영상별 댓글은 PostgreSQL investment_youtube_video_comments 에 저장.
    """

    __tablename__ = "investment_youtube_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    keyword = Column(String(255), nullable=True, index=True)     # parsed.company (None 가능)
    query_used = Column(String(255), nullable=False)             # 실제 검색 쿼리 (fallback 포함)
    video_count = Column(Integer, nullable=False, default=0)
    comment_count = Column(Integer, nullable=False, default=0)
    keyword_count = Column(Integer, nullable=False, default=0)
    keywords_top = Column(JSON, nullable=False)                  # [{noun, count, rank}, ...]
    created_at = Column(DateTime, nullable=False, default=datetime.now, index=True)
