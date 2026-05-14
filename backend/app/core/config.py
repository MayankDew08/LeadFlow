from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from .env file."""

    # ─── Database ─────────────────────────────────────────────────────────────
    database_url: str = Field("sqlite+aiosqlite:///./leadflow.db", validation_alias="DATABASE_URL")

    # ─── Redis / Upstash ──────────────────────────────────────────────────────
    redis_url: str = Field(..., validation_alias="UPSTASH_REDIS_REST_URL")
    redis_token: str = Field("", validation_alias="UPSTASH_REDIS_REST_TOKEN")

    # ─── AI providers ─────────────────────────────────────────────────────────
    anthropic_api_key: str = Field("", validation_alias="ANTHROPIC_API_KEY")
    gemini_api_key: str = Field("", validation_alias="GEMINI_API_KEY")
    groq_api_key: str = Field("", validation_alias="GROQ_API_KEY")
    tavily_api_key: str = Field("", validation_alias="TAVILY_API_KEY")

    # ─── App ───────────────────────────────────────────────────────────────────
    environment: str = Field("development", validation_alias="ENVIRONMENT")

    # ─── Auth / JWT ───────────────────────────────────────────────────────────
    secret_key: str = Field("", validation_alias="SECRET_KEY")
    algorithm: str = Field("HS256", validation_alias="ALGORITHM")
    access_token_expire_minutes: int = Field(30, validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        populate_by_name=True,
        extra="ignore",
    )

    @property
    def async_database_url(self) -> str:
        """Return the database URL (SQLite is already async-ready, Postgres needs dialect)."""
        url = self.database_url.strip().strip('"').strip("'")
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance (singleton pattern)."""
    return Settings()


settings = get_settings()