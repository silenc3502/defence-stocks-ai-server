from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)

from app.infrastructure.database.session import Base


class InterestArticleORM(Base):
    """관심 기사 메타데이터 (MySQL)."""

    __tablename__ = "interest_articles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    title = Column(String(500), nullable=False)
    source = Column(String(255), nullable=True)
    link = Column(String(512), nullable=False)
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    __table_args__ = (
        UniqueConstraint(
            "account_id",
            "link",
            name="uq_interest_article_account_link",
        ),
    )
