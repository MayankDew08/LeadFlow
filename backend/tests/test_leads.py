import pytest
import uuid

@pytest.fixture
async def auth_token(client):
    """Fixture to get a valid auth token."""
    email = f"lead_test_{uuid.uuid4().hex[:6]}@example.com"
    password = "password"
    await client.post("/api/auth/register", json={
        "name": "Lead Tester",
        "email": email,
        "password": password
    })
    response = await client.post("/api/auth/login", data={
        "username": email,
        "password": password
    })
    return response.json()["access_token"]

@pytest.mark.asyncio
async def test_create_and_list_leads(client, auth_token):
    """Integration test: Verify lead creation and listing."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # 1. Create Lead
    lead_data = {
        "name": "John Doe",
        "company": "ACME Corp",
        "phone": "1234567890",
        "status": "New"
    }
    create_response = await client.post("/api/leads", json=lead_data, headers=headers)
    assert create_response.status_code == 201
    lead_id = create_response.json()["id"]
    
    # 2. List Leads
    list_response = await client.get("/api/leads", headers=headers)
    assert list_response.status_code == 200
    assert list_response.json()["total"] >= 1
    
    # 3. Get Lead by ID (via filter)
    filter_response = await client.get(f"/api/leads?lead_id={lead_id}", headers=headers)
    assert filter_response.status_code == 200
    assert filter_response.json()["leads"][0]["id"] == lead_id

@pytest.mark.asyncio
async def test_update_lead_status(client, auth_token):
    """Integration test: Verify lead status update."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # 1. Create Lead
    create_response = await client.post("/api/leads", json={
        "name": "Jane Smith",
        "status": "New"
    }, headers=headers)
    lead_id = create_response.json()["id"]
    
    # 2. Update Status
    update_response = await client.patch(f"/api/leads/{lead_id}", json={
        "status": "Qualified"
    }, headers=headers)
    assert update_response.status_code == 204
    
    # 3. Verify Update
    verify_response = await client.get(f"/api/leads?lead_id={lead_id}", headers=headers)
    assert verify_response.json()["leads"][0]["status"] == "Qualified"
