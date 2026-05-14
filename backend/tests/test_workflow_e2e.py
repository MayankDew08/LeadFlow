import pytest
import uuid

@pytest.mark.asyncio
async def test_full_lead_lifecycle_e2e(client):
    """E2E Scenario: Full Lead Lifecycle from registration to deletion."""
    
    # 1. Register & Login
    email = f"e2e_{uuid.uuid4().hex[:6]}@example.com"
    await client.post("/api/auth/register", json={
        "name": "E2E Specialist",
        "email": email,
        "password": "password123"
    })
    login_res = await client.post("/api/auth/login", data={
        "username": email,
        "password": "password123"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Create Lead
    lead_res = await client.post("/api/leads", json={
        "name": "Target Company",
        "company": "Big Tech",
        "status": "New"
    }, headers=headers)
    lead_id = lead_res.json()["id"]
    
    # 3. Add a discussion note
    await client.post(f"/api/leads/{lead_id}/discussions", json={
        "note": "First contact made. Interested.",
        "follow_up_at": None
    }, headers=headers)
    
    # 4. Use AI to score the lead
    score_res = await client.post("/api/ai/score-lead", json={"lead_id": lead_id}, headers=headers)
    # Even if it's 503, we continue as it's an optional enhancement
    
    # 5. Update lead status based on "interest"
    await client.patch(f"/api/leads/{lead_id}", json={"status": "Qualified"}, headers=headers)
    
    # 6. Verify lead state
    verify_res = await client.get(f"/api/leads?lead_id={lead_id}", headers=headers)
    assert verify_res.json()["leads"][0]["status"] == "Qualified"
    
    # 7. Delete Lead
    del_res = await client.delete(f"/api/leads/{lead_id}", headers=headers)
    assert del_res.status_code == 204
    
    # 8. Confirm Deletion
    confirm_res = await client.get(f"/api/leads?lead_id={lead_id}", headers=headers)
    assert confirm_res.json()["total"] == 0
