from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings


# SQLite async engine (uses aiosqlite)
database_url = settings.async_database_url

engine = create_async_engine(
    database_url,
    echo=settings.environment == "development",
    connect_args={"check_same_thread": False},
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