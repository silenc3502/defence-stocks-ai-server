from fastapi import Depends

from app.domains.auth.adapter.outbound.in_memory.session_repository import SessionRepository
from app.domains.auth.adapter.outbound.in_memory.session_repository_impl import SessionRepositoryImpl
from app.domains.market_video.adapter.outbound.external.market_video_client import MarketVideoClient
from app.domains.market_video.adapter.outbound.external.market_video_port import MarketVideoPort
from app.domains.market_video.application.usecase.list_market_video_usecase import ListMarketVideoUseCase
from app.infrastructure.cache.redis_client import get_redis


def get_session_repository() -> SessionRepository:
    return SessionRepositoryImpl(get_redis())


def get_market_video_port() -> MarketVideoPort:
    return MarketVideoClient()


def get_list_market_video_usecase(
    market_video_port: MarketVideoPort = Depends(get_market_video_port),
) -> ListMarketVideoUseCase:
    return ListMarketVideoUseCase(market_video_port)
