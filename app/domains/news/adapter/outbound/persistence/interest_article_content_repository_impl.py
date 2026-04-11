from typing import Any, Dict

from sqlalchemy.orm import Session

from app.domains.news.adapter.outbound.persistence.interest_article_content_repository import (
    InterestArticleContentRepository,
)
from app.domains.news.infrastructure.orm.interest_article_content_orm import (
    InterestArticleContentORM,
)


class InterestArticleContentRepositoryImpl(InterestArticleContentRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(
        self,
        article_id: int,
        account_id: int,
        link: str,
        raw: Dict[str, Any],
    ) -> None:
        orm = InterestArticleContentORM(
            id=article_id,
            account_id=account_id,
            link=link,
            raw=raw,
        )
        self.db.add(orm)
        self.db.commit()

    def delete(self, article_id: int) -> None:
        self.db.query(InterestArticleContentORM).filter(
            InterestArticleContentORM.id == article_id
        ).delete()
        self.db.commit()
