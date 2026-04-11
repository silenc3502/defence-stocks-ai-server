from fastapi import Depends

from app.domains.auth.adapter.outbound.in_memory.session_repository import SessionRepository
from app.domains.auth.adapter.outbound.in_memory.session_repository_impl import (
    SessionRepositoryImpl,
)
from app.domains.news.adapter.outbound.external.news_search_port import (
    NewsSearchPort,
)
from app.domains.news.adapter.outbound.external.serp_news_search_client import (
    SerpNewsSearchClient,
)
from app.domains.news.application.usecase.search_news_usecase import (
    SearchNewsUseCase,
)
from app.infrastructure.cache.redis_client import get_redis
from app.infrastructure.external.serp.serp_api_client import serp_api_client


def get_news_search_port() -> NewsSearchPort:
    return SerpNewsSearchClient(serp_api_client)


def get_search_news_usecase(
    news_search_port: NewsSearchPort = Depends(get_news_search_port),
) -> SearchNewsUseCase:
    return SearchNewsUseCase(news_search_port)


def get_session_repository() -> SessionRepository:
    return SessionRepositoryImpl(get_redis())
