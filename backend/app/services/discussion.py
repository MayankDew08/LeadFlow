from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.discussion import Discussion
from app.schemas.discussion import DiscussionCreate


def _lead_id_value(lead_id: UUID) -> str:
    return str(lead_id)


# ── Get All Discussions For a Lead ────────────────────────────────────────────
async def get_discussions(
    db: AsyncSession,
    lead_id: UUID,
) -> tuple[list[Discussion], int]:
    result = await db.execute(
        select(Discussion)
        .filter(Discussion.lead_id == _lead_id_value(lead_id))
        .order_by(Discussion.created_at.desc())
    )
    discussions = result.scalars().all()
    return discussions, len(discussions)


# ── Create Discussion ────────────────────────────────────────────────────────
async def create_discussion(
    db: AsyncSession,
    lead_id: UUID,
    payload: DiscussionCreate,
) -> Discussion:
    discussion = Discussion(
        lead_id=_lead_id_value(lead_id),
        note=payload.note,
        follow_up_at=payload.follow_up_at,
    )
    db.add(discussion)
    await db.commit()
    await db.refresh(discussion)
    return discussion