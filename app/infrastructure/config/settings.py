from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    mysql_user: str
    mysql_password: str
    mysql_host: str
    mysql_port: int
    mysql_schema: str

    postgres_host: str
    postgres_port: int
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_pool_size: int = 5
    postgres_max_overflow: int = 10

    kakao_client_id: str
    kakao_redirect_uri: str

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str
    session_expire_minutes: int = 1440

    cors_allowed_frontend_url: str

    youtube_api_key: str

    openai_api_key: str

    serp_api_key: str
    serp_api_base_url: str = "https://serpapi.com"
    serp_api_default_engine: str = "google_news"
    serp_api_timeout_seconds: float = 10.0
    serp_api_max_retries: int = 3

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
