import sys
from pathlib import Path

# Add backend directory to sys.path to resolve 'app' module
sys.path.append(str(Path(__file__).parent.parent))

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.core.database import AsyncSessionLocal, get_db

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="session")
async def db_session() -> AsyncSession:
    """Fixture to get a live DB session."""
    async with AsyncSessionLocal() as session:
        yield session

@pytest.fixture(scope="session")
async def client(db_session):
    """Fixture for an async client that uses the live DB session."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()
