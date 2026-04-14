from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.domains.investment.adapter.outbound.persistence.investment_youtube_video_comment_repository import (
    InvestmentYoutubeVideoCommentRepository,
)
from app.domains.investment.infrastructure.orm.investment_youtube_video_comment_orm import (
    InvestmentYoutubeVideoCommentORM,
)


class InvestmentYoutubeVideoCommentRepositoryImpl(
    InvestmentYoutubeVideoCommentRepository
):
    def __init__(self, db: Session):
        self.db = db

    def save(
        self,
        video_pk: int,
        video_id: str,
        comments: List[Dict[str, Any]],
    ) -> None:
        orm = InvestmentYoutubeVideoCommentORM(
            id=video_pk,
            video_id=video_id,
            comments=comments,
        )
        self.db.add(orm)
        self.db.commit()

    def find_by_video_pk(self, video_pk: int) -> Optional[List[Dict[str, Any]]]:
        orm = (
            self.db.query(InvestmentYoutubeVideoCommentORM)
            .filter(InvestmentYoutubeVideoCommentORM.id == video_pk)
            .first()
        )
        return orm.comments if orm else None
