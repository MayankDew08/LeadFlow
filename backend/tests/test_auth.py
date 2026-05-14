import pytest
import uuid

@pytest.mark.asyncio
async def test_register_and_login(client):
    """Integration test: Verify user registration and login flow."""
    random_id = str(uuid.uuid4())[:8]
    email = f"test_{random_id}@example.com"
    password = "testpassword123"
    
    # 1. Register
    reg_response = await client.post("/api/auth/register", json={
        "name": "Test User",
        "email": email,
        "password": password
    })
    assert reg_response.status_code == 201
    assert reg_response.json()["email"] == email
    
    # 2. Login
    # Note: Login uses form-data (application/x-www-form-urlencoded)
    login_response = await client.post("/api/auth/login", data={
        "username": email,
        "password": password
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    assert token is not None
    
    # 3. Get Me
    me_response = await client.get("/api/auth/me", headers={
        "Authorization": f"Bearer {token}"
    })
    assert me_response.status_code == 200
    assert me_response.json()["email"] == email

@pytest.mark.asyncio
async def test_login_invalid_credentials(client):
    """Integration test: Verify login fails with wrong password."""
    response = await client.post("/api/auth/login", data={
        "username": "nonexistent@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
