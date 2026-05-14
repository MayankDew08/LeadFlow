from uuid import UUID
import logging
import time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.discussion import Discussion
from app.schemas.discussion import DiscussionCreate
from app.core.log_format import JSONFormatter

# Setup logging
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger = logging.getLogger("discussion_service")
if not logger.handlers:
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


def _lead_id_value(lead_id: UUID) -> str:
    return str(lead_id)


# ── Get All Discussions For a Lead ────────────────────────────────────────────
async def get_discussions(
    db: AsyncSession,
    lead_id: UUID,
) -> tuple[list[Discussion], int]:
    """Fetch all discussions for a lead with logging."""
    start_time = time.time()
    try:
        result = await db.execute(
            select(Discussion)
            .filter(Discussion.lead_id == _lead_id_value(lead_id))
            .order_by(Discussion.created_at.desc())
        )
        discussions = result.scalars().all()
        
        elapsed = (time.time() - start_time) * 1000
        logger.info({
            "event": "discussions_fetched",
            "lead_id": str(lead_id),
            "count": len(discussions),
            "duration_ms": round(elapsed, 2),
            "status": "success"
        })
        return discussions, len(discussions)
    except Exception as e:
        elapsed = (time.time() - start_time) * 1000
        logger.error({
            "event": "discussions_fetch_failed",
            "lead_id": str(lead_id),
            "error": str(e),
            "duration_ms": round(elapsed, 2),
            "status": "failure"
        })
        raise


# ── Create Discussion ────────────────────────────────────────────────────────
async def create_discussion(
    db: AsyncSession,
    lead_id: UUID,
    payload: DiscussionCreate,
) -> Discussion:
    """Create a new discussion with logging."""
    start_time = time.time()
    try:
        discussion = Discussion(
            lead_id=_lead_id_value(lead_id),
            note=payload.note,
            follow_up_at=payload.follow_up_at,
        )
        db.add(discussion)
        await db.commit()
        await db.refresh(discussion)
        
        elapsed = (time.time() - start_time) * 1000
        logger.info({
            "event": "discussion_created",
            "lead_id": str(lead_id),
            "discussion_id": str(discussion.id),
            "has_followup": payload.follow_up_at is not None,
            "duration_ms": round(elapsed, 2),
            "status": "success"
        })
        return discussion
    except Exception as e:
        elapsed = (time.time() - start_time) * 1000
        logger.error({
            "event": "discussion_creation_failed",
            "lead_id": str(lead_id),
            "error": str(e),
            "duration_ms": round(elapsed, 2),
            "status": "failure"
        })
        raise