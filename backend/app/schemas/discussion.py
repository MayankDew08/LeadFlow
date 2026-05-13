from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional


# ── Request Schemas ───────────────────────────────────────────────────────────
class DiscussionCreate(BaseModel):
    note: str = Field(..., min_length=1)
    follow_up_at: Optional[datetime] = None


# ── Response Schemas ──────────────────────────────────────────────────────────
class DiscussionResponse(BaseModel):
    id: UUID
    lead_id: UUID
    note: str
    follow_up_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class DiscussionListResponse(BaseModel):
    discussions: list[DiscussionResponse]
    total: int