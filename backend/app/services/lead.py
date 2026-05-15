from uuid import UUID
from typing import Optional
from datetime import datetime, timezone
import logging
import time

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, func, or_, select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.models.lead import Lead
from app.models.discussion import Discussion
from app.schemas.lead import LeadCreate, LeadUpdate
from app.core.log_format import JSONFormatter
from app.core.exceptions import DatabaseError, NotFoundError, ValidationError, DuplicateResourceError

# Setup logging
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger = logging.getLogger("lead_service")
if not logger.handlers:
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


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
    """Fetch leads with optional filtering. Logs operation with timing."""
    start_time = time.time()
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
        today = datetime.now(timezone.utc).date()
        filters.append(func.date(Lead.follow_up_at) == today)
        filters.append(Lead.status.notin_(["Won", "Lost"]))

    query = select(Lead)
    if filters:
        query = query.where(and_(*filters))

    query = query.order_by(Lead.created_at.desc())

    try:
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

        elapsed = (time.time() - start_time) * 1000
        logger.info({
            "event": "leads_fetched",
            "count": len(leads),
            "filters": {
                "lead_id": str(lead_id) if lead_id else None,
                "status": status,
                "company": company is not None,
                "phone": phone is not None,
                "follow_up_today": follow_up_today
            },
            "duration_ms": round(elapsed, 2),
            "status": "success"
        })
        return leads, len(leads)
    except SQLAlchemyError as e:
        elapsed = (time.time() - start_time) * 1000
        logger.error({
            "event": "leads_fetch_database_error",
            "error": str(e),
            "error_type": "SQLAlchemyError",
            "duration_ms": round(elapsed, 2),
            "status": "failure"
        })
        raise DatabaseError(f"Failed to fetch leads: {str(e)}")
    except Exception as e:
        elapsed = (time.time() - start_time) * 1000
        logger.error({
            "event": "leads_fetch_failed",
            "error": str(e),
            "error_type": type(e).__name__,
            "duration_ms": round(elapsed, 2),
            "status": "failure"
        })
        raise


# ── Get Single Lead ──────────────────────────────────────────────────────────
async def get_lead_by_id(db: AsyncSession, lead_id: UUID) -> Optional[Lead]:
    """Fetch a single lead by ID with logging and error handling."""
    start_time = time.time()
    try:
        if not lead_id:
            raise ValidationError("Lead ID is required")
        
        result = await db.execute(select(Lead).filter(Lead.id == _lead_id_value(lead_id)))
        lead = result.scalar_one_or_none()
        
        elapsed = (time.time() - start_time) * 1000
        if lead:
            logger.info({
                "event": "lead_fetched",
                "lead_id": str(lead_id),
                "found": True,
                "duration_ms": round(elapsed, 2),
                "status": "success"
            })
        else:
            logger.warning({
                "event": "lead_not_found",
                "lead_id": str(lead_id),
                "duration_ms": round(elapsed, 2),
                "status": "not_found"
            })
        return lead
    except ValidationError as e:
        elapsed = (time.time() - start_time) * 1000
        logger.error({
            "event": "lead_fetch_validation_error",
            "lead_id": str(lead_id),
            "error": str(e),
            "duration_ms": round(elapsed, 2),
            "status": "failure"
        })
        raise
    except SQLAlchemyError as e:
        elapsed = (time.time() - start_time) * 1000
        logger.error({
            "event": "lead_fetch_database_error",
            "lead_id": str(lead_id),
            "error": str(e),
            "error_type": "SQLAlchemyError",
            "duration_ms": round(elapsed, 2),
            "status": "failure"
        })
        raise DatabaseError(f"Failed to fetch lead {lead_id}: {str(e)}")
    except Exception as e:
        elapsed = (time.time() - start_time) * 1000
        logger.error({
            "event": "lead_fetch_error",
            "lead_id": str(lead_id),
            "error": str(e),
            "error_type": type(e).__name__,
            "duration_ms": round(elapsed, 2),
            "status": "error"
        })
        raise DatabaseError(f"Unexpected error fetching lead: {str(e)}")


# ── Create Lead ──────────────────────────────────────────────────────────────
async def create_lead(db: AsyncSession, payload: LeadCreate, sales_rep_id: str | None = None) -> Lead:
    """Create a new lead with logging."""
    start_time = time.time()
    try:
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
        
        elapsed = (time.time() - start_time) * 1000
        logger.info({
            "event": "lead_created",
            "lead_id": str(lead.id),
            "name": payload.name,
            "company": payload.company,
            "status": payload.status.value,
            "sales_rep_id": sales_rep_id,
            "duration_ms": round(elapsed, 2),
            "status": "success"
        })
        return lead
    except Exception as e:
        elapsed = (time.time() - start_time) * 1000
        logger.error({
            "event": "lead_creation_failed",
            "name": payload.name,
            "error": str(e),
            "duration_ms": round(elapsed, 2),
            "status": "failure"
        })
        raise


# ── Update Lead ──────────────────────────────────────────────────────────────
async def update_lead(db: AsyncSession, lead: Lead, payload: LeadUpdate) -> Lead:
    """Update an existing lead with logging."""
    start_time = time.time()
    try:
        update_data = payload.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if hasattr(value, "value"):
                value = value.value
            setattr(lead, field, value)

        lead.updated_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(lead)
        
        elapsed = (time.time() - start_time) * 1000
        logger.info({
            "event": "lead_updated",
            "lead_id": str(lead.id),
            "fields_updated": list(update_data.keys()),
            "duration_ms": round(elapsed, 2),
            "status": "success"
        })
        return lead
    except Exception as e:
        elapsed = (time.time() - start_time) * 1000
        logger.error({
            "event": "lead_update_failed",
            "lead_id": str(lead.id),
            "error": str(e),
            "duration_ms": round(elapsed, 2),
            "status": "failure"
        })
        raise


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
        lead.updated_at = datetime.now(timezone.utc)
        await db.commit()


# ── Delete Lead ──────────────────────────────────────────────────────────────
async def delete_lead(db: AsyncSession, lead: Lead) -> None:
    """Delete a lead with logging."""
    start_time = time.time()
    try:
        lead_id = str(lead.id)
        await db.delete(lead)
        await db.commit()
        
        elapsed = (time.time() - start_time) * 1000
        logger.info({
            "event": "lead_deleted",
            "lead_id": lead_id,
            "duration_ms": round(elapsed, 2),
            "status": "success"
        })
    except Exception as e:
        elapsed = (time.time() - start_time) * 1000
        logger.error({
            "event": "lead_deletion_failed",
            "lead_id": str(lead.id),
            "error": str(e),
            "duration_ms": round(elapsed, 2),
            "status": "failure"
        })
        raise