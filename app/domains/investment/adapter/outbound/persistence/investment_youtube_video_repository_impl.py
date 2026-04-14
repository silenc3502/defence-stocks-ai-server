from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.domains.investment.adapter.outbound.persistence.investment_youtube_video_repository import (
    InvestmentYoutubeVideoRepository,
)
from app.domains.investment.infrastructure.orm.investment_youtube_video_orm import (
    InvestmentYoutubeVideoORM,
)


class InvestmentYoutubeVideoRepositoryImpl(InvestmentYoutubeVideoRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(
        self,
        log_id: int,
        video_id: str,
        title: str,
        channel_name: Optional[str],
        video_url: str,
        thumbnail_url: Optional[str],
        published_at: Optional[datetime],
        comment_count: int,
    ) -> int:
        orm = InvestmentYoutubeVideoORM(
            log_id=log_id,
            video_id=video_id,
            title=title,
            channel_name=channel_name,
            video_url=video_url,
            thumbnail_url=thumbnail_url,
            published_at=published_at,
            comment_count=comment_count,
        )
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return orm.id
