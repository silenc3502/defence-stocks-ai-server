from fastapi import Depends
from sqlalchemy.orm import Session

from app.domains.auth.adapter.outbound.in_memory.session_repository import SessionRepository
from app.domains.auth.adapter.outbound.in_memory.session_repository_impl import (
    SessionRepositoryImpl,
)
from app.domains.news.adapter.outbound.external.article_content_fetcher import (
    ArticleContentFetcher,
)
from app.domains.news.adapter.outbound.external.httpx_article_content_fetcher import (
    HttpxArticleContentFetcher,
)
from app.domains.news.adapter.outbound.external.news_search_port import (
    NewsSearchPort,
)
from app.domains.news.adapter.outbound.external.serp_news_search_client import (
    SerpNewsSearchClient,
)
from app.domains.news.adapter.outbound.persistence.interest_article_content_repository import (
    InterestArticleContentRepository,
)
from app.domains.news.adapter.outbound.persistence.interest_article_content_repository_impl import (
    InterestArticleContentRepositoryImpl,
)
from app.domains.news.adapter.outbound.persistence.interest_article_repository import (
    InterestArticleRepository,
)
from app.domains.news.adapter.outbound.persistence.interest_article_repository_impl import (
    InterestArticleRepositoryImpl,
)
from app.domains.news.application.usecase.save_interest_article_usecase import (
    SaveInterestArticleUseCase,
)
from app.domains.news.application.usecase.search_news_usecase import (
    SearchNewsUseCase,
)
from app.infrastructure.cache.redis_client import get_redis
from app.infrastructure.database.postgres_session import get_postgres_db
from app.infrastructure.database.session import get_db
from app.infrastructure.external.serp.serp_api_client import serp_api_client


def get_news_search_port() -> NewsSearchPort:
    return SerpNewsSearchClient(serp_api_client)


def get_search_news_usecase(
    news_search_port: NewsSearchPort = Depends(get_news_search_port),
) -> SearchNewsUseCase:
    return SearchNewsUseCase(news_search_port)


def get_session_repository() -> SessionRepository:
    return SessionRepositoryImpl(get_redis())


def get_interest_article_repository(
    db: Session = Depends(get_db),
) -> InterestArticleRepository:
    return InterestArticleRepositoryImpl(db)


def get_interest_article_content_repository(
    db: Session = Depends(get_postgres_db),
) -> InterestArticleContentRepository:
    return InterestArticleContentRepositoryImpl(db)


def get_article_content_fetcher() -> ArticleContentFetcher:
    return HttpxArticleContentFetcher()


def get_save_interest_article_usecase(
    article_repository: InterestArticleRepository = Depends(get_interest_article_repository),
    content_repository: InterestArticleContentRepository = Depends(
        get_interest_article_content_repository
    ),
    content_fetcher: ArticleContentFetcher = Depends(get_article_content_fetcher),
) -> SaveInterestArticleUseCase:
    return SaveInterestArticleUseCase(
        article_repository,
        content_repository,
        content_fetcher,
    )
