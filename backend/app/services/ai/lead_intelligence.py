import json
import logging
import time
from datetime import datetime
from app.services.ai.clients import groq_client, GROQ_MODEL
from app.core.log_format import JSONFormatter

# Setup logging
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger = logging.getLogger("lead_intelligence_service")
if not logger.handlers:
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


# ── Helper: Strip JSON fences ────────────────────────────────────────────────
def parse_json_response(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.rsplit("```", 1)[0]
    return json.loads(text.strip())


# ── 1. SUMMARIZE LEAD ────────────────────────────────────────────────────────
async def summarize_lead(name: str, company: str, status: str, discussions: list) -> dict:
    """Generate AI brief from discussion history with logging."""
    start_time = time.time()
    logger.info({
        "event": "lead_summarization_started",
        "lead_name": name,
        "discussion_count": len(discussions)
    })

    discussion_text = "\n".join([
        f"- {d['created_at']}: {d['note']}" for d in discussions
    ])

    prompt = f"""Lead: {name} at {company or 'Unknown'}
Status: {status}

Discussion history (oldest to newest):
{discussion_text}

Return ONLY this JSON:
{{
  "situation": "1-2 sentence summary of where things stand",
  "concerns": ["concern 1", "concern 2"],
  "next_action": "concrete next step the sales rep should take"
}}"""

    try:
        response = await groq_client.chat.completions.create(
            model=GROQ_MODEL,
            max_tokens=500,
            temperature=0.3,
            messages=[
                {
                    "role": "system",
                    "content": "You are a CRM assistant for sales reps. Be concise and actionable. Return only valid JSON."
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},  # Groq enforces JSON
        )

        text = response.choices[0].message.content
        data = parse_json_response(text)
        data["ai_available"] = True
        
        elapsed = (time.time() - start_time) * 1000
        logger.info({
            "event": "lead_summarization_success",
            "lead_name": name,
            "duration_ms": round(elapsed, 2),
            "status": "success"
        })
        return data

    except Exception as e:
        elapsed = (time.time() - start_time) * 1000
        logger.error({
            "event": "lead_summarization_failed",
            "lead_name": name,
            "error": str(e),
            "duration_ms": round(elapsed, 2),
            "status": "failure"
        })
        return {
            "ai_available": False,
            "error": str(e),
            "situation": "AI summary unavailable",
            "concerns": [],
            "next_action": "Review discussion history manually",
        }


# ── 2. SUGGEST FOLLOW-UP ─────────────────────────────────────────────────────
async def suggest_followup(note: str) -> dict:
    """Extract follow-up date from discussion note with logging."""
    start_time = time.time()
    logger.info({"event": "followup_suggestion_started"})

    today = datetime.utcnow().strftime("%Y-%m-%d")

    prompt = f"""Today is {today}.
Discussion note: "{note}"

If the note implies a follow-up timing (like "next week", "in 3 days", "Friday at 2pm"), suggest a specific date/time.

Return ONLY this JSON:
{{
  "follow_up_iso": "2025-01-20T14:00:00" or null if no timing implied,
  "reasoning": "brief explanation of why this date"
}}"""

    try:
        response = await groq_client.chat.completions.create(
            model=GROQ_MODEL,
            max_tokens=300,
            temperature=0.2,
            messages=[
                {
                    "role": "system",
                    "content": "You are a scheduling assistant. Extract follow-up timing from sales notes. Return only valid JSON."
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
        )

        text = response.choices[0].message.content
        data = parse_json_response(text)
        data["ai_available"] = True
        
        elapsed = (time.time() - start_time) * 1000
        logger.info({
            "event": "followup_suggestion_success",
            "has_followup": data.get("follow_up_iso") is not None,
            "duration_ms": round(elapsed, 2),
            "status": "success"
        })
        return data

    except Exception as e:
        elapsed = (time.time() - start_time) * 1000
        logger.warning({
            "event": "followup_suggestion_failed",
            "error": str(e),
            "duration_ms": round(elapsed, 2),
            "status": "failure"
        })
        return {
            "ai_available": False,
            "error": str(e),
            "follow_up_iso": None,
            "reasoning": "AI suggestion unavailable",
        }


# ── 3. SCORE LEAD ────────────────────────────────────────────────────────────
async def score_lead(name: str, status: str, days_since_contact: int, latest_note: str) -> dict:
    """Score lead as Hot/Warm/Cold with logging."""
    start_time = time.time()
    logger.info({
        "event": "lead_scoring_started",
        "lead_name": name,
        "days_since_contact": days_since_contact
    })

    prompt = f"""Lead: {name}
Status: {status}
Days since last discussion: {days_since_contact}
Latest note: "{latest_note}"

Score this lead based on:
- Hot: high engagement, recent positive signals, ready to close
- Warm: active but not urgent, needs nurturing
- Cold: low engagement, stale, or showing disinterest

Return ONLY this JSON:
{{
  "score": "Hot" or "Warm" or "Cold",
  "reason": "1 sentence explanation"
}}"""

    try:
        response = await groq_client.chat.completions.create(
            model=GROQ_MODEL,
            max_tokens=200,
            temperature=0.3,
            messages=[
                {
                    "role": "system",
                    "content": "You are a lead scoring assistant. Return only valid JSON."
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
        )

        text = response.choices[0].message.content
        data = parse_json_response(text)
        data["ai_available"] = True
        
        elapsed = (time.time() - start_time) * 1000
        logger.info({
            "event": "lead_scoring_success",
            "lead_name": name,
            "score": data.get("score"),
            "duration_ms": round(elapsed, 2),
            "status": "success"
        })
        return data

    except Exception as e:
        elapsed = (time.time() - start_time) * 1000
        logger.warning({
            "event": "lead_scoring_failed",
            "lead_name": name,
            "error": str(e),
            "duration_ms": round(elapsed, 2),
            "status": "failure"
        })
        return {
            "ai_available": False,
            "error": str(e),
            "score": "Warm",
            "reason": "AI scoring unavailable",
        }