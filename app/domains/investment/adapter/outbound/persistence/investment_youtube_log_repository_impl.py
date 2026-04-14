from typing import List, Optional

from sqlalchemy.orm import Session

from app.domains.investment.adapter.outbound.persistence.investment_youtube_log_repository import (
    InvestmentYoutubeLogRepository,
)
from app.domains.investment.infrastructure.orm.investment_youtube_log_orm import (
    InvestmentYoutubeLogORM,
)


class InvestmentYoutubeLogRepositoryImpl(InvestmentYoutubeLogRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(
        self,
        keyword: Optional[str],
        query_used: str,
        video_count: int,
        comment_count: int,
        keyword_count: int,
        keywords_top: List[dict],
    ) -> int:
        orm = InvestmentYoutubeLogORM(
            keyword=keyword,
            query_used=query_used,
            video_count=video_count,
            comment_count=comment_count,
            keyword_count=keyword_count,
            keywords_top=keywords_top,
        )
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return orm.id
