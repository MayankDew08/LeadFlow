from uuid import UUID
from typing import Optional
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, func, or_, select

from app.models.lead import Lead
from app.models.discussion import Discussion
from app.schemas.lead import LeadCreate, LeadUpdate


def _lead_id_value(lead_id: UUID | str) -> str:
    return str(lead_id)



# ── Get All Leads (LATERAL JOIN for last discussion) ──────────────────────────
async def get_leads(
    db: AsyncSession,
    lead_id: Optional[UUID] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    company: Optional[str] = None,
    phone: Optional[str] = None,
    follow_up_today: bool = False,
) -> tuple[list[dict], int]:
    filters = []

    if lead_id:
        filters.append(Lead.id == _lead_id_value(lead_id))

    if status:
        filters.append(Lead.status == status)

    if company:
        company_term = company.strip().lower()
        if company_term:
            filters.append(func.lower(func.coalesce(Lead.company, "")).like(f"%{company_term}%"))

    if phone:
        phone_term = phone.strip().lower()
        if phone_term:
            filters.append(func.lower(func.coalesce(Lead.phone, "")).like(f"%{phone_term}%"))

    if search:
        term = search.strip().lower()
        if term:
            pattern = f"%{term}%"
            filters.append(
                or_(
                    func.lower(Lead.name).like(pattern),
                    func.lower(func.coalesce(Lead.company, "")).like(pattern),
                    func.lower(func.coalesce(Lead.phone, "")).like(pattern),
                    func.lower(Lead.status).like(pattern),
                    func.lower(Lead.id).like(pattern),
                )
            )

    if follow_up_today:
        today = datetime.now(timezone.utc).date().isoformat()
        filters.append(func.date(Lead.follow_up_at) == today)
        filters.append(Lead.status.notin_(["Won", "Lost"]))

    query = select(Lead)
    if filters:
        query = query.where(and_(*filters))

    query = query.order_by(Lead.created_at.desc())

    result = await db.execute(query)
    lead_rows = result.scalars().all()

    latest_discussion_map: dict[str, dict] = {}
    lead_ids = [lead.id for lead in lead_rows]

    if lead_ids:
        latest_times = (
            select(
                Discussion.lead_id.label("lead_id"),
                func.max(Discussion.created_at).label("last_discussion_at"),
            )
            .where(Discussion.lead_id.in_(lead_ids))
            .group_by(Discussion.lead_id)
            .subquery()
        )

        latest_rows = await db.execute(
            select(
                Discussion.lead_id,
                Discussion.note,
                Discussion.created_at,
            ).join(
                latest_times,
                and_(
                    Discussion.lead_id == latest_times.c.lead_id,
                    Discussion.created_at == latest_times.c.last_discussion_at,
                ),
            )
        )

        for row in latest_rows.all():
            latest_discussion_map[row.lead_id] = {
                "note": row.note,
                "created_at": row.created_at,
            }

    leads = []
    for row in lead_rows:
        lead = {
            "id": row.id,
            "name": row.name,
            "company": row.company,
            "phone": row.phone,
            "sales_rep_id": row.sales_rep_id,
            "status": row.status,
            "follow_up_at": row.follow_up_at,
            "created_at": row.created_at,
            "updated_at": row.updated_at,
            "last_discussion": latest_discussion_map.get(row.id),
        }
        leads.append(lead)

    return leads, len(leads)


# ── Get Single Lead ──────────────────────────────────────────────────────────
async def get_lead_by_id(db: AsyncSession, lead_id: UUID) -> Optional[Lead]:
    result = await db.execute(select(Lead).filter(Lead.id == _lead_id_value(lead_id)))
    return result.scalar_one_or_none()


# ── Create Lead ──────────────────────────────────────────────────────────────
async def create_lead(db: AsyncSession, payload: LeadCreate, sales_rep_id: str | None = None) -> Lead:
    lead = Lead(
        name=payload.name,
        company=payload.company,
        phone=payload.phone,
        status=payload.status.value,
        sales_rep_id=sales_rep_id,
    )
    db.add(lead)
    await db.commit()
    await db.refresh(lead)
    return lead


# ── Update Lead ──────────────────────────────────────────────────────────────
async def update_lead(db: AsyncSession, lead: Lead, payload: LeadUpdate) -> Lead:
    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if hasattr(value, "value"):
            value = value.value
        setattr(lead, field, value)

    lead.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(lead)
    return lead


# ── Update Lead follow_up_at (called when discussion sets a follow-up) ───────
async def update_lead_follow_up(
    db: AsyncSession,
    lead_id: UUID,
    follow_up_at: datetime,
) -> None:
    result = await db.execute(select(Lead).filter(Lead.id == _lead_id_value(lead_id)))
    lead = result.scalar_one_or_none()
    if lead:
        lead.follow_up_at = follow_up_at
        lead.updated_at = datetime.utcnow()
        await db.commit()


# ── Delete Lead ──────────────────────────────────────────────────────────────
async def delete_lead(db: AsyncSession, lead: Lead) -> None:
    await db.delete(lead)
    await db.commit()