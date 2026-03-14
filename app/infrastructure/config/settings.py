from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    mysql_user: str
    mysql_password: str
    mysql_host: str
    mysql_port: int
    mysql_schema: str

    kakao_client_id: str
    kakao_redirect_uri: str

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
