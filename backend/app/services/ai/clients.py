from groq import AsyncGroq
import google.generativeai as genai
from tavily import AsyncTavilyClient
from dotenv import load_dotenv

from app.core.config import settings

load_dotenv()

# ── Groq ─────────────────────────────────────────────────────────────────────
groq_client = AsyncGroq(api_key=settings.groq_api_key)
GROQ_MODEL = "llama-3.3-70b-versatile"

# ── Gemini ───────────────────────────────────────────────────────────────────
genai.configure(api_key=settings.gemini_api_key)
GEMINI_MODEL = "gemini-1.5-pro"

# ── Tavily (fallback search) ─────────────────────────────────────────────────
tavily_client = AsyncTavilyClient(api_key=settings.tavily_api_key)