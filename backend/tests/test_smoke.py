import pytest

@pytest.mark.asyncio
async def test_health_check(client):
    """Smoke test: Verify health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "leadflow-api"}

@pytest.mark.asyncio
async def test_root_endpoint(client):
    """Smoke test: Verify root endpoint."""
    response = await client.get("/")
    assert response.status_code == 200
    assert "Welcome" in response.json()["message"]
