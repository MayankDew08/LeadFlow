from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings


# Database async engine
database_url = settings.async_database_url
is_sqlite = database_url.startswith("sqlite")
is_postgres = database_url.startswith("postgresql")

connect_args = {}
if is_sqlite:
    connect_args["check_same_thread"] = False
if is_postgres:
    # Supabase/PgBouncer fixes:
    # Disable prepared statements if using transaction pooling (common in Supabase)
    connect_args["statement_cache_size"] = 0

engine = create_async_engine(
    database_url,
    echo=settings.environment == "development",
    connect_args=connect_args,
    future=True,
)


# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


async def get_db():
    """Async dependency to get database session."""
    async with AsyncSessionLocal() as session:
        yield session