from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import JSONB

from app.infrastructure.database.postgres_session import PostgresBase


class InvestmentNewsContentORM(PostgresBase):
    """투자 워크플로우가 수집한 뉴스 본문 (PostgreSQL JSONB).

    `id` = MySQL `investment_news.id` 와 동일한 값 (cross-DB 키).
    `raw` JSONB 에는 ArticleContentFetcher 의 fetch 결과 전체가 저장된다
    (url, final_url, status_code, content_type, fetched_at, extracted_title, text, html).
    """

    __tablename__ = "investment_news_contents"

    id = Column(Integer, primary_key=True, autoincrement=False)
    link = Column(String(512), nullable=False)
    raw = Column(JSONB, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
