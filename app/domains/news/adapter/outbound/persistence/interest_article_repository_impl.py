from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.domains.news.adapter.outbound.persistence.interest_article_repository import (
    InterestArticleRepository,
)
from app.domains.news.infrastructure.orm.interest_article_orm import InterestArticleORM


class InterestArticleRepositoryImpl(InterestArticleRepository):
    def __init__(self, db: Session):
        self.db = db

    def exists(self, account_id: int, link: str) -> bool:
        return (
            self.db.query(InterestArticleORM.id)
            .filter(
                InterestArticleORM.account_id == account_id,
                InterestArticleORM.link == link,
            )
            .first()
            is not None
        )

    def save(
        self,
        account_id: int,
        title: str,
        source: Optional[str],
        link: str,
        published_at: Optional[datetime],
    ) -> int:
        orm = InterestArticleORM(
            account_id=account_id,
            title=title,
            source=source,
            link=link,
            published_at=published_at,
        )
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return orm.id

    def delete(self, article_id: int) -> None:
        self.db.query(InterestArticleORM).filter(
            InterestArticleORM.id == article_id
        ).delete()
        self.db.commit()
