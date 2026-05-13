from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.discussion import DiscussionCreate, DiscussionResponse, DiscussionListResponse
from app.services.discussion import get_discussions, create_discussion
from app.services.lead import get_lead_by_id, update_lead_follow_up

router = APIRouter(prefix="/leads", tags=["discussions"])


# ── GET /leads/{id}/discussions ───────────────────────────────────────────────
@router.get("/{lead_id}/discussions", response_model=DiscussionListResponse)
async def list_discussions(
    lead_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    lead = await get_lead_by_id(db=db, lead_id=lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    discussions, total = await get_discussions(db=db, lead_id=lead_id)
    return {"discussions": discussions, "total": total}


# ── POST /leads/{id}/discussions ──────────────────────────────────────────────
@router.post(
    "/{lead_id}/discussions",
    response_model=DiscussionResponse,
    status_code=201,
)
async def create_new_discussion(
    lead_id: UUID,
    payload: DiscussionCreate,
    db: AsyncSession = Depends(get_db),
):
    lead = await get_lead_by_id(db=db, lead_id=lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    discussion = await create_discussion(db=db, lead_id=lead_id, payload=payload)

    # ── Propagate follow_up_at to lead ────────────────────────────────────────
    if payload.follow_up_at:
        await update_lead_follow_up(
            db=db,
            lead_id=lead_id,
            follow_up_at=payload.follow_up_at,
        )

    return discussion