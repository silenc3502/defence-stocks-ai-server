from typing import Optional

from sqlalchemy.orm import Session

from app.domains.market_video.adapter.outbound.persistence.market_video_repository import MarketVideoRepository
from app.domains.market_video.domain.entity.market_video import MarketVideo
from app.domains.market_video.infrastructure.mapper.market_video_mapper import MarketVideoMapper
from app.domains.market_video.infrastructure.orm.market_video_orm import MarketVideoORM


class MarketVideoRepositoryImpl(MarketVideoRepository):
    def __init__(self, db: Session):
        self.db = db

    def find_by_video_id(self, video_id: str) -> Optional[MarketVideo]:
        orm = self.db.query(MarketVideoORM).filter(MarketVideoORM.video_id == video_id).first()
        if orm is None:
            return None
        return MarketVideoMapper.to_entity(orm)

    def save(self, entity: MarketVideo) -> MarketVideo:
        orm = MarketVideoMapper.to_orm(entity)
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return MarketVideoMapper.to_entity(orm)

    def update(self, entity: MarketVideo) -> MarketVideo:
        orm = self.db.query(MarketVideoORM).filter(MarketVideoORM.video_id == entity.video_id).first()
        orm.title = entity.title
        orm.channel_name = entity.channel_name
        orm.published_at = entity.published_at
        orm.view_count = entity.view_count
        orm.thumbnail_url = entity.thumbnail_url
        orm.video_url = entity.video_url
        self.db.commit()
        self.db.refresh(orm)
        return MarketVideoMapper.to_entity(orm)

    def delete_all(self) -> None:
        self.db.query(MarketVideoORM).delete()
        self.db.commit()

    def find_all_ordered_by_published_at(self, limit: int) -> list[MarketVideo]:
        orms = (
            self.db.query(MarketVideoORM)
            .order_by(MarketVideoORM.published_at.desc())
            .limit(limit)
            .all()
        )
        return [MarketVideoMapper.to_entity(orm) for orm in orms]
