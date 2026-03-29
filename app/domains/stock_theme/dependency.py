from fastapi import Depends
from sqlalchemy.orm import Session

from app.domains.auth.adapter.outbound.in_memory.session_repository import SessionRepository
from app.domains.auth.adapter.outbound.in_memory.session_repository_impl import SessionRepositoryImpl
from app.domains.market_video.adapter.outbound.persistence.market_video_repository_impl import MarketVideoRepositoryImpl
from app.domains.market_video.adapter.outbound.persistence.video_comment_repository_impl import VideoCommentRepositoryImpl
from app.domains.stock_theme.adapter.outbound.persistence.defence_stock_repository import DefenceStockRepository
from app.domains.stock_theme.adapter.outbound.persistence.defence_stock_repository_impl import DefenceStockRepositoryImpl
from app.domains.stock_theme.application.usecase.list_defence_stocks_usecase import ListDefenceStocksUseCase
from app.domains.stock_theme.application.usecase.recommend_stocks_usecase import RecommendStocksUseCase
from app.infrastructure.cache.redis_client import get_redis
from app.infrastructure.database.session import get_db
from app.infrastructure.llm.llm_port import LLMPort
from app.infrastructure.llm.openai_client import OpenAIClient


def get_session_repository() -> SessionRepository:
    return SessionRepositoryImpl(get_redis())


def get_defence_stock_repository(db: Session = Depends(get_db)) -> DefenceStockRepository:
    return DefenceStockRepositoryImpl(db)


def get_list_defence_stocks_usecase(
    defence_stock_repository: DefenceStockRepository = Depends(get_defence_stock_repository),
) -> ListDefenceStocksUseCase:
    return ListDefenceStocksUseCase(defence_stock_repository)


def get_llm_port() -> LLMPort:
    return OpenAIClient()


def get_recommend_stocks_usecase(
    db: Session = Depends(get_db),
    llm_port: LLMPort = Depends(get_llm_port),
) -> RecommendStocksUseCase:
    return RecommendStocksUseCase(
        market_video_repository=MarketVideoRepositoryImpl(db),
        video_comment_repository=VideoCommentRepositoryImpl(db),
        defence_stock_repository=DefenceStockRepositoryImpl(db),
        llm_port=llm_port,
    )
