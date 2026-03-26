from app.domains.market_video.domain.entity.market_video import MarketVideo
from app.domains.market_video.infrastructure.orm.market_video_orm import MarketVideoORM


class MarketVideoMapper:
    @staticmethod
    def to_orm(entity: MarketVideo) -> MarketVideoORM:
        return MarketVideoORM(
            video_id=entity.video_id,
            title=entity.title,
            channel_name=entity.channel_name,
            published_at=entity.published_at,
            view_count=entity.view_count,
            thumbnail_url=entity.thumbnail_url,
            video_url=entity.video_url,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @staticmethod
    def to_entity(orm: MarketVideoORM) -> MarketVideo:
        return MarketVideo(
            id=orm.id,
            video_id=orm.video_id,
            title=orm.title,
            channel_name=orm.channel_name,
            published_at=orm.published_at,
            view_count=orm.view_count,
            thumbnail_url=orm.thumbnail_url,
            video_url=orm.video_url,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )
