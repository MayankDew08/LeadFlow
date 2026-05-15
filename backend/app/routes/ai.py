from uuid import UUID
import logging
import time
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.core.database import get_db
from app.core.log_format import JSONFormatter
from app.core.exceptions import (
    DatabaseError, NotFoundError, ValidationError,
    AIServiceError, ExternalServiceError
)
from app.routes.auth import get_current_user
from app.models.user import User
from app.services.ai.company_enrichment import enrich_company
from app.services.ai.lead_intelligence import (
    summarize_lead,
    suggest_followup,
    score_lead,
)
from app.services.lead import get_lead_by_id
from app.services.discussion import get_discussions
from pydantic import BaseModel
from app.services.ai.email_generator import generate_email, EmailGenerationError
from app.schemas.ai import EmailGenerateRequest, EmailGenerateResponse

# Setup logging
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger = logging.getLogger("ai_routes")
if not logger.handlers:
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


router = APIRouter(prefix="/ai", tags=["ai"])


# ── Helper: Convert exceptions to HTTP responses ──────────────────────────────
def _exception_to_http_status(exc: Exception) -> int:
    """Map exception types to appropriate HTTP status codes."""
    if isinstance(exc, ValidationError):
        return status.HTTP_422_UNPROCESSABLE_ENTITY
    elif isinstance(exc, NotFoundError):
        return status.HTTP_404_NOT_FOUND
    elif isinstance(exc, (DatabaseError, AIServiceError, ExternalServiceError)):
        return status.HTTP_503_SERVICE_UNAVAILABLE
    else:
        return status.HTTP_500_INTERNAL_SERVER_ERROR


# ── Schemas ──────────────────────────────────────────────────────────────────
class EnrichRequest(BaseModel):
    company_name: str


class SummarizeRequest(BaseModel):
    lead_id: UUID


class FollowupRequest(BaseModel):
    note: str


class ScoreRequest(BaseModel):
    lead_id: UUID


# ── 1. Enrich Company ────────────────────────────────────────────────────────
@router.post("/enrich-company")
async def enrich(
    payload: EnrichRequest,
    current_user: User = Depends(get_current_user),
):
    start_time = time.time()
    try:
        if not payload.company_name or not payload.company_name.strip():
            logger.warning({
                "event": "enrich_company_validation_failed",
                "reason": "empty_company_name"
            })
            raise ValidationError("Company name cannot be empty")
        
        logger.info({
            "event": "enrich_company_request",
            "user_id": str(current_user.id),
            "company": payload.company_name
        })
        
        result = await enrich_company(payload.company_name.strip())
        elapsed = (time.time() - start_time) * 1000
        logger.info({
            "event": "enrich_company_response",
            "company": payload.company_name,
            "ai_available": result.get("ai_available"),
            "source": result.get("source"),
            "duration_ms": round(elapsed, 2),
            "status": "success"
        })
        return result
    except ValidationError as e:
        elapsed = (time.time() - start_time) * 1000
        logger.warning({
            "event": "enrich_company_validation_error",
            "error": str(e),
            "duration_ms": round(elapsed, 2),
            "status": "validation_error"
        })
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except (ExternalServiceError, AIServiceError) as e:
        elapsed = (time.time() - start_time) * 1000
        logger.error({
            "event": "enrich_company_service_error",
            "error": str(e),
            "error_type": type(e).__name__,
            "duration_ms": round(elapsed, 2),
            "status": "service_error"
        })
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="AI service temporarily unavailable")
    except Exception as e:
        elapsed = (time.time() - start_time) * 1000
        logger.error({
            "event": "enrich_company_error",
            "error": str(e),
            "error_type": type(e).__name__,
            "duration_ms": round(elapsed, 2),
            "status": "error"
        })
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


# ── 2. Summarize Lead ────────────────────────────────────────────────────────
@router.post("/summarize")
async def summarize(
    payload: SummarizeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    start_time = time.time()
    try:
        if not payload.lead_id:
            raise ValidationError("Lead ID is required")
        
        logger.info({
            "event": "summarize_lead_request",
            "user_id": str(current_user.id),
            "lead_id": str(payload.lead_id)
        })
        
        lead = await get_lead_by_id(db=db, lead_id=payload.lead_id)
        if not lead:
            elapsed = (time.time() - start_time) * 1000
            logger.warning({
                "event": "summarize_lead_not_found",
                "lead_id": str(payload.lead_id),
                "duration_ms": round(elapsed, 2)
            })
            raise NotFoundError(f"Lead {payload.lead_id} not found")

        discussions, _ = await get_discussions(db=db, lead_id=payload.lead_id)
        
        # Reverse to chronological order (oldest first)
        discussions_list = [
            {"created_at": d.created_at.isoformat(), "note": d.note}
            for d in reversed(discussions)
        ]

        result = await summarize_lead(
            name=lead.name,
            company=lead.company or "",
            status=lead.status,
            discussions=discussions_list,
        )
        
        elapsed = (time.time() - start_time) * 1000
        logger.info({
            "event": "summarize_lead_response",
            "lead_id": str(payload.lead_id),
            "lead_name": lead.name,
            "discussion_count": len(discussions),
            "ai_available": result.get("ai_available"),
            "duration_ms": round(elapsed, 2),
            "status": "success"
        })
        return result
    except ValidationError as e:
        elapsed = (time.time() - start_time) * 1000
        logger.warning({
            "event": "summarize_lead_validation_error",
            "error": str(e),
            "duration_ms": round(elapsed, 2)
        })
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except NotFoundError as e:
        elapsed = (time.time() - start_time) * 1000
        logger.warning({
            "event": "summarize_lead_not_found_error",
            "lead_id": str(payload.lead_id),
            "error": str(e),
            "duration_ms": round(elapsed, 2)
        })
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (DatabaseError, AIServiceError) as e:
        elapsed = (time.time() - start_time) * 1000
        logger.error({
            "event": "summarize_lead_service_error",
            "error": str(e),
            "error_type": type(e).__name__,
            "duration_ms": round(elapsed, 2)
        })
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Service temporarily unavailable")
    except Exception as e:
        elapsed = (time.time() - start_time) * 1000
        logger.error({
            "event": "summarize_lead_error",
            "lead_id": str(payload.lead_id),
            "error": str(e),
            "error_type": type(e).__name__,
            "duration_ms": round(elapsed, 2),
            "status": "error"
        })
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


# ── 3. Suggest Follow-up ─────────────────────────────────────────────────────
@router.post("/suggest-followup")
async def suggest(
    payload: FollowupRequest,
    current_user: User = Depends(get_current_user),
):
    start_time = time.time()
    try:
        if not payload.note or not payload.note.strip():
            raise ValidationError("Note cannot be empty")
        
        logger.info({
            "event": "suggest_followup_request",
            "user_id": str(current_user.id)
        })
        
        result = await suggest_followup(payload.note.strip())
        elapsed = (time.time() - start_time) * 1000
        logger.info({
            "event": "suggest_followup_response",
            "has_followup": result.get("follow_up_iso") is not None,
            "ai_available": result.get("ai_available"),
            "duration_ms": round(elapsed, 2),
            "status": "success"
        })
        return result
    except ValidationError as e:
        elapsed = (time.time() - start_time) * 1000
        logger.warning({
            "event": "suggest_followup_validation_error",
            "error": str(e),
            "duration_ms": round(elapsed, 2)
        })
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except (AIServiceError, ExternalServiceError) as e:
        elapsed = (time.time() - start_time) * 1000
        logger.error({
            "event": "suggest_followup_service_error",
            "error": str(e),
            "error_type": type(e).__name__,
            "duration_ms": round(elapsed, 2)
        })
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="AI service temporarily unavailable")
    except Exception as e:
        elapsed = (time.time() - start_time) * 1000
        logger.error({
            "event": "suggest_followup_error",
            "error": str(e),
            "error_type": type(e).__name__,
            "duration_ms": round(elapsed, 2),
            "status": "error"
        })
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


# ── 4. Score Lead ────────────────────────────────────────────────────────────
@router.post("/score-lead")
async def score(
    payload: ScoreRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    start_time = time.time()
    try:
        if not payload.lead_id:
            raise ValidationError("Lead ID is required")
        
        logger.info({
            "event": "score_lead_request",
            "user_id": str(current_user.id),
            "lead_id": str(payload.lead_id)
        })
        
        lead = await get_lead_by_id(db=db, lead_id=payload.lead_id)
        if not lead:
            elapsed = (time.time() - start_time) * 1000
            logger.warning({
                "event": "score_lead_not_found",
                "lead_id": str(payload.lead_id),
                "duration_ms": round(elapsed, 2)
            })
            raise NotFoundError(f"Lead {payload.lead_id} not found")

        discussions, _ = await get_discussions(db=db, lead_id=payload.lead_id)
        
        if not discussions:
            elapsed = (time.time() - start_time) * 1000
            logger.info({
                "event": "score_lead_no_discussions",
                "lead_id": str(payload.lead_id),
                "duration_ms": round(elapsed, 2),
                "status": "no_data"
            })
            return {
                "score": "Cold",
                "reason": "No discussions yet",
                "ai_available": True,
            }

        latest = discussions[0]
        days_since = (datetime.now(timezone.utc) - latest.created_at).days

        result = await score_lead(
            name=lead.name,
            status=lead.status,
            days_since_contact=days_since,
            latest_note=latest.note,
        )
        
        elapsed = (time.time() - start_time) * 1000
        logger.info({
            "event": "score_lead_response",
            "lead_id": str(payload.lead_id),
            "lead_name": lead.name,
            "score": result.get("score"),
            "ai_available": result.get("ai_available"),
            "duration_ms": round(elapsed, 2),
            "status": "success"
        })
        return result
    except ValidationError as e:
        elapsed = (time.time() - start_time) * 1000
        logger.warning({
            "event": "score_lead_validation_error",
            "error": str(e),
            "duration_ms": round(elapsed, 2)
        })
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except NotFoundError as e:
        elapsed = (time.time() - start_time) * 1000
        logger.warning({
            "event": "score_lead_not_found_error",
            "error": str(e),
            "duration_ms": round(elapsed, 2)
        })
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (DatabaseError, AIServiceError) as e:
        elapsed = (time.time() - start_time) * 1000
        logger.error({
            "event": "score_lead_service_error",
            "error": str(e),
            "error_type": type(e).__name__,
            "duration_ms": round(elapsed, 2)
        })
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Service temporarily unavailable")
    except Exception as e:
        elapsed = (time.time() - start_time) * 1000
        logger.error({
            "event": "score_lead_error",
            "lead_id": str(payload.lead_id),
            "error": str(e),
            "error_type": type(e).__name__,
            "duration_ms": round(elapsed, 2),
            "status": "error"
        })
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/generate-email", response_model=EmailGenerateResponse)
async def generate_email_endpoint(
    payload: EmailGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    start_time = time.time()
    try:
        if not payload.lead_id:
            raise ValidationError("Lead ID is required")
        if not payload.purpose or not payload.tone:
            raise ValidationError("Purpose and tone are required")
        
        logger.info({
            "event": "generate_email_request",
            "user_id": str(current_user.id),
            "lead_id": str(payload.lead_id),
            "purpose": payload.purpose.value
        })
        
        # ── Verify lead exists ──────────────────────────────────────────────────
        lead = await get_lead_by_id(db=db, lead_id=payload.lead_id)
        if not lead:
            elapsed = (time.time() - start_time) * 1000
            logger.warning({
                "event": "generate_email_lead_not_found",
                "lead_id": str(payload.lead_id),
                "duration_ms": round(elapsed, 2)
            })
            raise NotFoundError(f"Lead {payload.lead_id} not found")
        
        # ── Generate email with fallback chain ──────────────────────────────────
        result = await generate_email(
            lead_name=lead.name,
            company=lead.company or "",
            status=lead.status,
            purpose=payload.purpose.value,
            context=payload.context or "",
            sender_name=current_user.name,
            tone=payload.tone.value,
        )
        
        elapsed = (time.time() - start_time) * 1000
        logger.info({
            "event": "generate_email_response",
            "lead_id": str(payload.lead_id),
            "lead_name": lead.name,
            "ai_available": result.get("ai_available"),
            "source": result.get("source"),
            "duration_ms": round(elapsed, 2),
            "status": "success"
        })
        return result
    except ValidationError as e:
        elapsed = (time.time() - start_time) * 1000
        logger.warning({
            "event": "generate_email_validation_error",
            "error": str(e),
            "duration_ms": round(elapsed, 2)
        })
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except NotFoundError as e:
        elapsed = (time.time() - start_time) * 1000
        logger.warning({
            "event": "generate_email_not_found_error",
            "error": str(e),
            "duration_ms": round(elapsed, 2)
        })
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except EmailGenerationError as e:
        elapsed = (time.time() - start_time) * 1000
        logger.error({
            "event": "generate_email_service_error",
            "lead_id": str(payload.lead_id),
            "error": str(e),
            "error_type": type(e).__name__,
            "duration_ms": round(elapsed, 2)
        })
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Email generation service temporarily unavailable")
    except (DatabaseError, AIServiceError) as e:
        elapsed = (time.time() - start_time) * 1000
        logger.error({
            "event": "generate_email_service_error",
            "error": str(e),
            "error_type": type(e).__name__,
            "duration_ms": round(elapsed, 2)
        })
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Service temporarily unavailable")
    except Exception as e:
        elapsed = (time.time() - start_time) * 1000
        logger.error({
            "event": "generate_email_error",
            "lead_id": str(payload.lead_id),
            "error": str(e),
            "error_type": type(e).__name__,
            "duration_ms": round(elapsed, 2),
            "status": "error"
        })
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")