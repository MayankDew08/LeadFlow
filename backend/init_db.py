#!/usr/bin/env python3
"""Initialize database tables."""
import asyncio
from sqlalchemy import text
from app.core.database import engine, Base
from app.models.lead import Lead
from app.models.discussion import Discussion
from app.models.user import User


async def init_db():
    """Create all database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # Drop existing tables (fresh start)
        await conn.run_sync(Base.metadata.create_all)  # Create tables
    print("✅ SQLite database initialized successfully!")
    print("📁 Database file: ./leadflow.db")


if __name__ == "__main__":
    asyncio.run(init_db())
