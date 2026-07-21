from functools import lru_cache

from pydantic import PostgresDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables or backend/.env."""

    app_name: str = "TableSwap API"
    environment: str = "development"
    database_url: PostgresDsn
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7
    openai_api_key: SecretStr | None = None
    openai_model: str = "gpt-5.6"
    openai_timeout_seconds: float = 20.0
    supabase_url: str | None = None
    supabase_service_role_key: SecretStr | None = None
    supabase_storage_bucket: str = "meal-images"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
