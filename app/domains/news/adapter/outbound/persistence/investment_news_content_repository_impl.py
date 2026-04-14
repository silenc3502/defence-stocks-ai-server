from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.domains.news.adapter.outbound.persistence.investment_news_content_repository import (
    InvestmentNewsContentRepository,
)
from app.domains.news.infrastructure.orm.investment_news_content_orm import (
    InvestmentNewsContentORM,
)


class InvestmentNewsContentRepositoryImpl(InvestmentNewsContentRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(self, news_id: int, link: str, raw: Dict[str, Any]) -> None:
        orm = InvestmentNewsContentORM(id=news_id, link=link, raw=raw)
        self.db.add(orm)
        self.db.commit()

    def find_by_id(self, news_id: int) -> Optional[Dict[str, Any]]:
        orm = (
            self.db.query(InvestmentNewsContentORM)
            .filter(InvestmentNewsContentORM.id == news_id)
            .first()
        )
        return orm.raw if orm else None
