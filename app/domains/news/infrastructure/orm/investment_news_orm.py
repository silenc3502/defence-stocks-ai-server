from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from app.infrastructure.database.session import Base


class InvestmentNewsORM(Base):
    """투자 워크플로우가 수집한 뉴스 메타데이터 (MySQL).

    이 테이블의 `id` 가 PostgreSQL `investment_news_contents` 의 cross-DB 키.
    """

    __tablename__ = "investment_news"

    id = Column(Integer, primary_key=True, autoincrement=True)
    keyword = Column(String(255), nullable=True, index=True)   # parsed.company (None 가능)
    query_used = Column(String(255), nullable=False)           # 실제 검색 쿼리 (fallback 반영)
    title = Column(String(500), nullable=False)
    source = Column(String(255), nullable=True)
    link = Column(String(512), nullable=False)
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now, index=True)
