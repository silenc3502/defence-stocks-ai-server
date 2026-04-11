from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import JSONB

from app.infrastructure.database.postgres_session import PostgresBase


class InterestArticleContentORM(PostgresBase):
    """관심 기사 본문 및 비정형 원본 데이터 (PostgreSQL JSONB).

    `id` 는 MySQL `interest_articles.id` 와 동일한 값을 가진다.
    두 저장소는 서로 다른 DB 이므로 FK 로 묶지 않고 애플리케이션 레벨에서
    정합성을 보장한다.
    """

    __tablename__ = "interest_article_contents"

    id = Column(Integer, primary_key=True, autoincrement=False)
    account_id = Column(Integer, nullable=False, index=True)
    link = Column(String(512), nullable=False)
    raw = Column(JSONB, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
