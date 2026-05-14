import pytest
import uuid
from datetime import datetime, timedelta

@pytest.fixture
async def auth_token(client):
    """Fixture to get a valid auth token."""
    email = f"disc_test_{uuid.uuid4().hex[:6]}@example.com"
    password = "password"
    await client.post("/api/auth/register", json={
        "name": "Discussion Tester",
        "email": email,
        "password": password
    })
    response = await client.post("/api/auth/login", data={
        "username": email,
        "password": password
    })
    return response.json()["access_token"]

@pytest.mark.asyncio
async def test_add_discussion_to_lead(client, auth_token):
    """Integration test: Verify adding a discussion to a lead."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # 1. Create Lead
    create_lead_res = await client.post("/api/leads", json={
        "name": "Discussion Lead",
        "status": "Contacted"
    }, headers=headers)
    lead_id = create_lead_res.json()["id"]
    
    # 2. Add Discussion
    follow_up = (datetime.utcnow() + timedelta(days=1)).isoformat()
    disc_data = {
        "note": "Had a great call, following up tomorrow.",
        "follow_up_at": follow_up
    }
    disc_res = await client.post(f"/api/leads/{lead_id}/discussions", json=disc_data, headers=headers)
    assert disc_res.status_code == 201
    assert disc_res.json()["note"] == disc_data["note"]
    
    # 3. List Discussions
    list_res = await client.get(f"/api/leads/{lead_id}/discussions", headers=headers)
    assert list_res.status_code == 200
    assert list_res.json()["total"] >= 1
    
    # 4. Verify Lead follow_up_at updated
    lead_res = await client.get(f"/api/leads?lead_id={lead_id}", headers=headers)
    assert lead_res.json()["leads"][0]["follow_up_at"] is not None
