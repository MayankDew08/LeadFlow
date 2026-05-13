from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from .env file."""

    # ─── Database ─────────────────────────────────────────────────────────────
    # SQLite database URL (default: ./leadflow.db)
    database_url: str = Field("sqlite+aiosqlite:///./leadflow.db", env="DATABASE_URL")

    # ─── Redis / Upstash ──────────────────────────────────────────────────────
    # Upstash REST API endpoint
    redis_url: str = Field(..., env="UPSTASH_REDIS_REST_URL", alias="upstash_redis_rest_url")
    # Upstash API token for authentication
    redis_token: str = Field("", env="UPSTASH_REDIS_REST_TOKEN", alias="upstash_redis_rest_token")

    # ─── Anthropic (Optional) ─────────────────────────────────────────────────
    # AI features degrade gracefully if not provided
    anthropic_api_key: str = Field("", env="ANTHROPIC_API_KEY")

    # ─── App ───────────────────────────────────────────────────────────────────
    environment: str = Field("development", env="ENVIRONMENT")

    # ─── Auth / JWT ───────────────────────────────────────────────────────────
    secret_key: str = Field("", env="SECRET_KEY")
    algorithm: str = Field("HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        populate_by_name=True,
    )

    @property
    def async_database_url(self) -> str:
        """Return the database URL (SQLite is already async-ready).

        Returns:
            str: The database URL.
        """
        return self.database_url.strip().strip('"').strip("'")
        return url


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance (singleton pattern)."""
    return Settings()


settings = get_settings()