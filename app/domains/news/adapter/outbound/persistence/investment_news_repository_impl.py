from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.domains.news.adapter.outbound.persistence.investment_news_repository import (
    InvestmentNewsRepository,
)
from app.domains.news.infrastructure.orm.investment_news_orm import InvestmentNewsORM


class InvestmentNewsRepositoryImpl(InvestmentNewsRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(
        self,
        keyword: Optional[str],
        query_used: str,
        title: str,
        source: Optional[str],
        link: str,
        published_at: Optional[datetime],
    ) -> int:
        orm = InvestmentNewsORM(
            keyword=keyword,
            query_used=query_used,
            title=title,
            source=source,
            link=link,
            published_at=published_at,
        )
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return orm.id

    def delete(self, news_id: int) -> None:
        self.db.query(InvestmentNewsORM).filter(InvestmentNewsORM.id == news_id).delete()
        self.db.commit()
