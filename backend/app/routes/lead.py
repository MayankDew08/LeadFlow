from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.lead import LeadCreate, LeadUpdate, LeadListResponse, LeadResponse
from app.services.lead import (
    get_leads,
    get_lead_by_id,
    create_lead,
    update_lead,
    delete_lead,
)
from app.routes.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/leads", tags=["leads"])


# ── GET /leads ────────────────────────────────────────────────────────────────
@router.get("", response_model=LeadListResponse)
async def list_leads(
    lead_id: Optional[UUID] = Query(None, description="Exact lead id to fetch"),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None, description="Search by name, company, phone, status, or id"),
    company: Optional[str] = Query(None, description="Filter by company name"),
    phone: Optional[str] = Query(None, description="Filter by phone number"),
    follow_up_today: bool = Query(False),
    db: AsyncSession = Depends(get_db),
):
    leads, total = await get_leads(
        db=db,
        lead_id=lead_id,
        status=status,
        search=search,
        company=company,
        phone=phone,
        follow_up_today=follow_up_today,
    )
    return {"leads": leads, "total": total}


# ── POST /leads ───────────────────────────────────────────────────────────────
@router.post("", response_model=LeadResponse, status_code=201)
async def create_new_lead(
    payload: LeadCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    lead = await create_lead(db=db, payload=payload, sales_rep_id=current_user.id)
    return lead


# ── PATCH /leads/{id} ─────────────────────────────────────────────────────────
@router.patch("/{lead_id}", status_code=204)
async def update_existing_lead(
    lead_id: UUID,
    payload: LeadUpdate,
    db: AsyncSession = Depends(get_db),
):
    lead = await get_lead_by_id(db=db, lead_id=lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    await update_lead(db=db, lead=lead, payload=payload)
    return None


# ── DELETE /leads/{id} ────────────────────────────────────────────────────────
@router.delete("/{lead_id}", status_code=204)
async def delete_existing_lead(
    lead_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    lead = await get_lead_by_id(db=db, lead_id=lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    await delete_lead(db=db, lead=lead)
    return None