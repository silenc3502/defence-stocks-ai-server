import logging
import urllib.parse

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base, sessionmaker

from app.infrastructure.config.settings import settings

logger = logging.getLogger(__name__)

_password = urllib.parse.quote_plus(settings.postgres_password)

POSTGRES_DATABASE_URL = (
    f"postgresql+psycopg2://{settings.postgres_user}:{_password}"
    f"@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"
)

postgres_engine = create_engine(
    POSTGRES_DATABASE_URL,
    pool_size=settings.postgres_pool_size,
    max_overflow=settings.postgres_max_overflow,
    pool_pre_ping=True,
    future=True,
)

PostgresSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=postgres_engine,
    future=True,
)

# 비정형 데이터(JSONB 등) ORM Model 전용 Declarative Base
# 도메인별 ORM Model은 이 Base를 상속하고
# sqlalchemy.dialects.postgresql.JSONB 컬럼을 사용한다.
PostgresBase = declarative_base()


def get_postgres_db():
    db = PostgresSessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_postgres_connection() -> None:
    """애플리케이션 기동 시 PostgreSQL 연결 가용성을 검증한다."""
    target = f"{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"
    try:
        with postgres_engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        logger.error("PostgreSQL 연결 실패 (%s): %s", target, exc)
        raise
    logger.info("PostgreSQL 연결 정상 (%s)", target)
