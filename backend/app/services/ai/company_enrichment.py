import json
import logging
import time
import google.generativeai as genai
from app.services.ai.clients import (
    groq_client,
    tavily_client,
    GROQ_MODEL,
    GEMINI_MODEL,
)
from app.core.log_format import JSONFormatter

# Setup logging
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger = logging.getLogger("company_enrichment_service")
if not logger.handlers:
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


# ─────────────────────────────────────────────────────────────────────────────
# PROMPTS
# ─────────────────────────────────────────────────────────────────────────────

GEMINI_PROMPT = """Research the company "{company_name}" using web search and return a JSON object with this EXACT structure:

{{
  "name": "Official company name",
  "industry": "Primary industry",
  "size": "Employee count range like '11-50' or '500+'",
  "website": "Official website URL",
  "headquarters": "City, Country",
  "founded": <year as number or null>,
  "description": "2-sentence summary",
  "recent_news": "1 sentence about recent news or null",
  "potential_pain_points": ["sales-relevant pain point 1", "pain point 2", "pain point 3"]
}}

Return ONLY the JSON object. No markdown, no commentary, no code fences.
If company cannot be verified, set unknown fields to null."""


GROQ_FORMAT_PROMPT = """You are given web search results about a company. Extract structured information into JSON.

Company name: {company_name}

Web search results:
{search_results}

Return ONLY this JSON structure (no markdown, no code fences):
{{
  "name": "Official company name",
  "industry": "Primary industry",
  "size": "Employee count range like '11-50' or '500+'",
  "website": "Official website URL",
  "headquarters": "City, Country",
  "founded": <year as number or null>,
  "description": "2-sentence summary based on search results",
  "recent_news": "1 sentence about recent news from search or null",
  "potential_pain_points": ["sales-relevant pain point 1", "pain point 2", "pain point 3"]
}}

If a field cannot be determined from search results, set it to null.
Pain points should be inferred from what the company does and current industry trends."""


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


def fallback_response(company_name: str, error: str = None) -> dict:
    """Final graceful fallback when all providers fail."""
    return {
        "ai_available": False,
        "name": company_name,
        "industry": None,
        "size": None,
        "website": None,
        "headquarters": None,
        "founded": None,
        "description": None,
        "recent_news": None,
        "potential_pain_points": [],
        "error": error or "AI enrichment unavailable",
        "source": "fallback",
    }


# ─────────────────────────────────────────────────────────────────────────────
# TIER 1: GEMINI WITH GOOGLE SEARCH
# ─────────────────────────────────────────────────────────────────────────────

async def _try_gemini(company_name: str) -> dict | None:
    """Try Gemini 1.5 Pro with native Google Search grounding. Returns None on failure."""
    start_time = time.time()
    try:
        logger.info({"event": "gemini_enrichment_started", "company": company_name, "tier": 1})
        
        model = genai.GenerativeModel(
            model_name=GEMINI_MODEL,
            tools="google_search_retrieval",
        )
        prompt = GEMINI_PROMPT.format(company_name=company_name)
        response = await model.generate_content_async(prompt)

        data = parse_json_response(response.text)
        data["ai_available"] = True
        data["source"] = "gemini"
        
        elapsed = (time.time() - start_time) * 1000
        logger.info({
            "event": "gemini_enrichment_success",
            "company": company_name,
            "tier": 1,
            "duration_ms": round(elapsed, 2),
            "status": "success"
        })
        return data

    except Exception as e:
        elapsed = (time.time() - start_time) * 1000
        logger.warning({
            "event": "gemini_enrichment_failed",
            "company": company_name,
            "tier": 1,
            "error": str(e),
            "duration_ms": round(elapsed, 2),
            "status": "failure"
        })
        return None


# ─────────────────────────────────────────────────────────────────────────────
# TIER 2: TAVILY SEARCH + GROQ FORMATTING
# ─────────────────────────────────────────────────────────────────────────────

async def _try_tavily_groq(company_name: str) -> dict | None:
    """Fallback: Tavily fetches web data, Groq formats it."""
    start_time = time.time()
    try:
        logger.info({"event": "tavily_groq_enrichment_started", "company": company_name, "tier": 2})
        
        # ── Step 1: Search the web with Tavily ──────────────────────────────
        search_query = (
            f"{company_name} company industry size headquarters "
            f"employees products news"
        )

        search_response = await tavily_client.search(
            query=search_query,
            search_depth="basic",
            max_results=5,
            include_answer=True,
        )

        # Compile search results into context
        results_text = ""
        if search_response.get("answer"):
            results_text += f"Summary: {search_response['answer']}\n\n"

        for i, result in enumerate(search_response.get("results", []), 1):
            results_text += (
                f"Source {i}: {result.get('title', '')}\n"
                f"URL: {result.get('url', '')}\n"
                f"Content: {result.get('content', '')[:500]}\n\n"
            )

        if not results_text.strip():
            logger.warning({
                "event": "tavily_search_no_results",
                "company": company_name,
                "tier": 2,
                "status": "no_data"
            })
            return None

        # ── Step 2: Format with Groq ────────────────────────────────────────
        prompt = GROQ_FORMAT_PROMPT.format(
            company_name=company_name,
            search_results=results_text[:4000],  # cap context size
        )

        response = await groq_client.chat.completions.create(
            model=GROQ_MODEL,
            max_tokens=600,
            temperature=0.3,
            messages=[
                {
                    "role": "system",
                    "content": "You extract structured company data from web search results. Return only valid JSON."
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
        )

        data = parse_json_response(response.choices[0].message.content)
        data["ai_available"] = True
        data["source"] = "tavily+groq"
        
        elapsed = (time.time() - start_time) * 1000
        logger.info({
            "event": "tavily_groq_enrichment_success",
            "company": company_name,
            "tier": 2,
            "duration_ms": round(elapsed, 2),
            "status": "success"
        })
        return data

    except Exception as e:
        elapsed = (time.time() - start_time) * 1000
        logger.warning({
            "event": "tavily_groq_enrichment_failed",
            "company": company_name,
            "tier": 2,
            "error": str(e),
            "duration_ms": round(elapsed, 2),
            "status": "failure"
        })
        return None


# ─────────────────────────────────────────────────────────────────────────────
# MAIN ENTRY POINT — ORCHESTRATES THE FALLBACK CHAIN
# ─────────────────────────────────────────────────────────────────────────────

async def enrich_company(company_name: str) -> dict:
    """
    Multi-tier company enrichment with graceful fallback.
    Logs each tier attempt with timing and success/failure status.
    
    Chain:
      1. Gemini + Google Search (primary)
      2. Tavily Search + Groq formatting (fallback)
      3. Empty response with ai_available=false (final)
    """
    start_time = time.time()
    logger.info({
        "event": "enrichment_started",
        "company": company_name,
        "status": "initiated"
    })

    # ── Tier 1 ──────────────────────────────────────────────────────────────
    result = await _try_gemini(company_name)
    if result:
        elapsed = (time.time() - start_time) * 1000
        logger.info({
            "event": "enrichment_complete",
            "company": company_name,
            "source": "gemini",
            "duration_ms": round(elapsed, 2),
            "status": "success"
        })
        return result

    # ── Tier 2 ──────────────────────────────────────────────────────────────
    logger.info({
        "event": "enrichment_fallback",
        "company": company_name,
        "from_tier": 1,
        "to_tier": 2,
        "status": "fallback"
    })
    result = await _try_tavily_groq(company_name)
    if result:
        elapsed = (time.time() - start_time) * 1000
        logger.info({
            "event": "enrichment_complete",
            "company": company_name,
            "source": "tavily+groq",
            "duration_ms": round(elapsed, 2),
            "status": "success"
        })
        return result

    # ── Tier 3 ──────────────────────────────────────────────────────────────
    elapsed = (time.time() - start_time) * 1000
    logger.error({
        "event": "enrichment_failed_all_tiers",
        "company": company_name,
        "duration_ms": round(elapsed, 2),
        "status": "failure"
    })
    return fallback_response(
        company_name,
        error="All enrichment providers temporarily unavailable",
    )