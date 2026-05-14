import json
import logging
import os
import time
import google.generativeai as genai
from app.services.ai.clients import groq_client, GROQ_MODEL, GEMINI_MODEL
from app.core.log_format import JSONFormatter

# Setup logging
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger = logging.getLogger("email_generator_service")
if not logger.handlers:
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


# ─────────────────────────────────────────────────────────────────────────────
# LOAD PROMPTS FROM FILE
# ─────────────────────────────────────────────────────────────────────────────

def _load_email_prompts():
    """Load EMAIL_SYSTEM and EMAIL_PROMPT from email_prompt.txt"""
    prompt_file = os.path.join(os.path.dirname(__file__), "email_prompt.txt")
    
    with open(prompt_file, 'r') as f:
        content = f.read()
    
    # Parse EMAIL_SYSTEM
    system_start = content.find('EMAIL_SYSTEM = """') + len('EMAIL_SYSTEM = """')
    system_end = content.find('"""', system_start)
    email_system = content[system_start:system_end].strip()
    
    # Parse EMAIL_PROMPT
    prompt_start = content.find('EMAIL_PROMPT = """') + len('EMAIL_PROMPT = """')
    prompt_end = content.find('"""', prompt_start)
    email_prompt = content[prompt_start:prompt_end].strip()
    
    return email_system, email_prompt


EMAIL_SYSTEM, EMAIL_PROMPT = _load_email_prompts()


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def parse_json_response(text: str) -> dict:
    """Strip code fences and parse JSON."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.rsplit("```", 1)[0]
    return json.loads(text.strip())


def build_prompt(
    lead_name: str,
    company: str,
    status: str,
    purpose: str,
    context: str,
    sender_name: str,
    tone: str,
) -> str:
    return EMAIL_PROMPT.format(
        name=lead_name,
        lead_name=lead_name,
        company=company or "their company",
        status=status,
        purpose=purpose,
        context=context or "No additional context provided",
        sender_name=sender_name,
        tone=tone,
    )


# ─────────────────────────────────────────────────────────────────────────────
# TIER 1: GROQ (FAST, PRIMARY)
# ─────────────────────────────────────────────────────────────────────────────

async def _try_groq(prompt: str) -> dict | None:
    """Try Groq for email generation. Returns None on failure."""
    start_time = time.time()
    try:
        logger.info({"event": "groq_email_generation_started", "tier": 1})
        
        response = await groq_client.chat.completions.create(
            model=GROQ_MODEL,
            max_tokens=600,
            temperature=0.7,  # Higher for creative writing
            messages=[
                {"role": "system", "content": EMAIL_SYSTEM},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
        )
        
        text = response.choices[0].message.content
        data = parse_json_response(text)
        
        # Validate required fields exist
        if not data.get("subject") or not data.get("body"):
            elapsed = (time.time() - start_time) * 1000
            logger.warning({
                "event": "groq_email_generation_invalid",
                "reason": "missing_fields",
                "tier": 1,
                "duration_ms": round(elapsed, 2),
                "status": "invalid_response"
            })
            return None
        
        data["ai_available"] = True
        data["source"] = "groq"
        
        elapsed = (time.time() - start_time) * 1000
        logger.info({
            "event": "groq_email_generation_success",
            "tier": 1,
            "duration_ms": round(elapsed, 2),
            "status": "success"
        })
        return data
        
    except Exception as e:
        elapsed = (time.time() - start_time) * 1000
        logger.warning({
            "event": "groq_email_generation_failed",
            "tier": 1,
            "error": str(e),
            "duration_ms": round(elapsed, 2),
            "status": "failure"
        })
        return None


# ─────────────────────────────────────────────────────────────────────────────
# TIER 2: GEMINI (FALLBACK)
# ─────────────────────────────────────────────────────────────────────────────

async def _try_gemini(prompt: str) -> dict | None:
    """Fallback: Try Gemini for email generation."""
    start_time = time.time()
    try:
        logger.info({"event": "gemini_email_generation_started", "tier": 2})
        
        model = genai.GenerativeModel(
            model_name=GEMINI_MODEL,
            system_instruction=EMAIL_SYSTEM,
        )
        
        response = await model.generate_content_async(prompt)
        text = response.text.strip()
        
        data = parse_json_response(text)
        
        # Validate required fields exist
        if not data.get("subject") or not data.get("body"):
            elapsed = (time.time() - start_time) * 1000
            logger.warning({
                "event": "gemini_email_generation_invalid",
                "reason": "missing_fields",
                "tier": 2,
                "duration_ms": round(elapsed, 2),
                "status": "invalid_response"
            })
            return None
        
        data["ai_available"] = True
        data["source"] = "gemini"
        
        elapsed = (time.time() - start_time) * 1000
        logger.info({
            "event": "gemini_email_generation_success",
            "tier": 2,
            "duration_ms": round(elapsed, 2),
            "status": "success"
        })
        return data
        
    except Exception as e:
        elapsed = (time.time() - start_time) * 1000
        logger.warning({
            "event": "gemini_email_generation_failed",
            "tier": 2,
            "error": str(e),
            "duration_ms": round(elapsed, 2),
            "status": "failure"
        })
        return None


# ─────────────────────────────────────────────────────────────────────────────
# MAIN ENTRY POINT — FALLBACK CHAIN
# ─────────────────────────────────────────────────────────────────────────────

class EmailGenerationError(Exception):
    """Raised when all AI providers fail to generate an email."""
    pass


async def generate_email(
    lead_name: str,
    company: str,
    status: str,
    purpose: str,
    context: str = "",
    sender_name: str = "the team",
    tone: str = "professional",
) -> dict:
    """
    Generate a sales email with multi-tier fallback.
    Logs each tier attempt with timing and success/failure status.
    
    Chain:
      1. Groq (fast, primary)
      2. Gemini (fallback)
      3. Raises EmailGenerationError if both fail
    """
    start_time = time.time()
    logger.info({
        "event": "email_generation_started",
        "lead_name": lead_name,
        "status": "initiated"
    })
    
    prompt = build_prompt(
        lead_name=lead_name,
        company=company,
        status=status,
        purpose=purpose,
        context=context,
        sender_name=sender_name,
        tone=tone,
    )
    
    # ── Tier 1: Groq ────────────────────────────────────────────────────────
    result = await _try_groq(prompt)
    if result:
        elapsed = (time.time() - start_time) * 1000
        logger.info({
            "event": "email_generation_complete",
            "lead_name": lead_name,
            "source": "groq",
            "duration_ms": round(elapsed, 2),
            "status": "success"
        })
        return result
    
    # ── Tier 2: Gemini ──────────────────────────────────────────────────────
    logger.info({
        "event": "email_generation_fallback",
        "lead_name": lead_name,
        "from_tier": 1,
        "to_tier": 2,
        "status": "fallback"
    })
    result = await _try_gemini(prompt)
    if result:
        elapsed = (time.time() - start_time) * 1000
        logger.info({
            "event": "email_generation_complete",
            "lead_name": lead_name,
            "source": "gemini",
            "duration_ms": round(elapsed, 2),
            "status": "success"
        })
        return result
    
    # ── Both failed → raise ─────────────────────────────────────────────────
    elapsed = (time.time() - start_time) * 1000
    logger.error({
        "event": "email_generation_failed_all_tiers",
        "lead_name": lead_name,
        "duration_ms": round(elapsed, 2),
        "status": "failure"
    })
    raise EmailGenerationError(
        "Email generation temporarily unavailable. Please try again later."
    )