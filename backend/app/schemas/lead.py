from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from uuid import UUID
from typing import Optional
from enum import Enum


# ── Status Enum ───────────────────────────────────────────────────────────────
class LeadStatus(str, Enum):
    NEW = "New"
    CONTACTED = "Contacted"
    QUALIFIED = "Qualified"
    PROPOSAL_SENT = "Proposal Sent"
    WON = "Won"
    LOST = "Lost"


# ── Nested Schema (last discussion preview on lead card) ──────────────────────
class LastDiscussion(BaseModel):
    note: str
    created_at: datetime

    class Config:
        from_attributes = True


# ── Request Schemas ───────────────────────────────────────────────────────────
class LeadCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    company: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    status: LeadStatus = LeadStatus.NEW

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name cannot be blank or whitespace")
        return v.strip()


class LeadUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    company: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    status: Optional[LeadStatus] = None
    # NOTE: follow_up_at is intentionally excluded
    # It is only updated via discussion creation


# ── Response Schemas ──────────────────────────────────────────────────────────
class LeadResponse(BaseModel):
    """Response schema for a single Lead.
    
    All database-generated fields have defaults to handle cases where
    the ORM hasn't yet persisted them (e.g., before commit).
    """
    id: Optional[UUID] = None
    name: str
    company: Optional[str] = None
    phone: Optional[str] = None
    sales_rep_id: Optional[UUID] = None
    status: LeadStatus
    follow_up_at: Optional[datetime] = None
    last_discussion: Optional[LastDiscussion] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LeadListResponse(BaseModel):
    leads: list[LeadResponse]
    total: int