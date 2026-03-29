from fastapi import Depends
from sqlalchemy.orm import Session

from app.domains.auth.adapter.outbound.in_memory.session_repository import SessionRepository
from app.domains.auth.adapter.outbound.in_memory.session_repository_impl import SessionRepositoryImpl
from app.domains.market_analysis.application.usecase.ask_analysis_usecase import AskAnalysisUseCase
from app.domains.market_video.adapter.outbound.persistence.market_video_repository_impl import MarketVideoRepositoryImpl
from app.domains.market_video.adapter.outbound.persistence.video_comment_repository_impl import VideoCommentRepositoryImpl
from app.domains.stock_theme.adapter.outbound.persistence.defence_stock_repository_impl import DefenceStockRepositoryImpl
from app.infrastructure.cache.redis_client import get_redis
from app.infrastructure.database.session import get_db


def get_session_repository() -> SessionRepository:
    return SessionRepositoryImpl(get_redis())


def get_ask_analysis_usecase(
    db: Session = Depends(get_db),
) -> AskAnalysisUseCase:
    return AskAnalysisUseCase(
        market_video_repository=MarketVideoRepositoryImpl(db),
        video_comment_repository=VideoCommentRepositoryImpl(db),
        defence_stock_repository=DefenceStockRepositoryImpl(db),
    )
