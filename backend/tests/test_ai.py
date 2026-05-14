import pytest
import uuid

@pytest.fixture
async def auth_token(client):
    """Fixture to get a valid auth token."""
    email = f"ai_test_{uuid.uuid4().hex[:6]}@example.com"
    password = "password"
    await client.post("/api/auth/register", json={
        "name": "AI Tester",
        "email": email,
        "password": password
    })
    response = await client.post("/api/auth/login", data={
        "username": email,
        "password": password
    })
    return response.json()["access_token"]

@pytest.mark.asyncio
async def test_enrich_company(client, auth_token):
    """Integration test: Verify AI company enrichment."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = await client.post("/api/ai/enrich-company", json={
        "company_name": "Google"
    }, headers=headers)
    # 503 if AI keys are missing/invalid, but usually we return 200 with ai_available=False
    assert response.status_code in [200, 503]
    if response.status_code == 200:
        data = response.json()
        assert "name" in data
        assert "ai_available" in data

@pytest.mark.asyncio
async def test_suggest_followup(client, auth_token):
    """Integration test: Verify AI follow-up suggestion."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = await client.post("/api/ai/suggest-followup", json={
        "note": "Meeting scheduled for next Tuesday at 2pm"
    }, headers=headers)
    assert response.status_code in [200, 503]
    if response.status_code == 200:
        assert "follow_up_iso" in response.json()

@pytest.mark.asyncio
async def test_summarize_and_score_lead(client, auth_token):
    """Integration test: Verify AI lead summarization and scoring."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # 1. Create Lead
    lead_res = await client.post("/api/leads", json={
        "name": "AI Lead",
        "company": "OpenAI",
        "status": "Qualified"
    }, headers=headers)
    lead_id = lead_res.json()["id"]
    
    # 2. Add Discussion (to give AI context)
    await client.post(f"/api/leads/{lead_id}/discussions", json={
        "note": "Intersted in our enterprise plan. Requested a demo."
    }, headers=headers)
    
    # 3. Summarize
    sum_res = await client.post("/api/ai/summarize", json={"lead_id": lead_id}, headers=headers)
    assert sum_res.status_code in [200, 503]
    
    # 4. Score
    score_res = await client.post("/api/ai/score-lead", json={"lead_id": lead_id}, headers=headers)
    assert score_res.status_code in [200, 503]

@pytest.mark.asyncio
async def test_generate_email(client, auth_token):
    """Integration test: Verify AI email generation."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # 1. Create Lead
    lead_res = await client.post("/api/leads", json={
        "name": "Email Target",
        "status": "New"
    }, headers=headers)
    lead_id = lead_res.json()["id"]
    
    # 2. Generate Email
    email_res = await client.post("/api/ai/generate-email", json={
        "lead_id": lead_id,
        "purpose": "introduction",
        "tone": "professional"
    }, headers=headers)
    assert email_res.status_code in [200, 503]
    if email_res.status_code == 200:
        assert "subject" in email_res.json()
        assert "body" in email_res.json()
