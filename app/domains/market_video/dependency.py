from fastapi import Depends
from sqlalchemy.orm import Session

from app.domains.auth.adapter.outbound.in_memory.session_repository import SessionRepository
from app.domains.auth.adapter.outbound.in_memory.session_repository_impl import SessionRepositoryImpl
from app.domains.market_video.adapter.outbound.external.market_video_client import MarketVideoClient
from app.domains.market_video.adapter.outbound.external.market_video_port import MarketVideoPort
from app.domains.market_video.adapter.outbound.persistence.market_video_repository import MarketVideoRepository
from app.domains.market_video.adapter.outbound.persistence.market_video_repository_impl import MarketVideoRepositoryImpl
from app.domains.market_video.adapter.outbound.persistence.video_comment_repository import VideoCommentRepository
from app.domains.market_video.adapter.outbound.persistence.video_comment_repository_impl import VideoCommentRepositoryImpl
from app.domains.market_video.application.usecase.collect_video_comments_usecase import CollectVideoCommentsUseCase
from app.domains.market_video.application.usecase.list_market_video_usecase import ListMarketVideoUseCase
from app.infrastructure.cache.redis_client import get_redis
from app.infrastructure.database.session import get_db


def get_session_repository() -> SessionRepository:
    return SessionRepositoryImpl(get_redis())


def get_market_video_port() -> MarketVideoPort:
    return MarketVideoClient()


def get_market_video_repository(db: Session = Depends(get_db)) -> MarketVideoRepository:
    return MarketVideoRepositoryImpl(db)


def get_list_market_video_usecase(
    market_video_port: MarketVideoPort = Depends(get_market_video_port),
    market_video_repository: MarketVideoRepository = Depends(get_market_video_repository),
) -> ListMarketVideoUseCase:
    return ListMarketVideoUseCase(market_video_port, market_video_repository)


def get_video_comment_repository(db: Session = Depends(get_db)) -> VideoCommentRepository:
    return VideoCommentRepositoryImpl(db)


def get_collect_video_comments_usecase(
    market_video_port: MarketVideoPort = Depends(get_market_video_port),
    market_video_repository: MarketVideoRepository = Depends(get_market_video_repository),
    video_comment_repository: VideoCommentRepository = Depends(get_video_comment_repository),
) -> CollectVideoCommentsUseCase:
    return CollectVideoCommentsUseCase(market_video_port, market_video_repository, video_comment_repository)
