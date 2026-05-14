from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional
from enum import Enum


class EmailPurpose(str, Enum):
    INTRODUCTION = "introduction"
    FOLLOW_UP = "follow-up"
    PROPOSAL = "proposal"
    CHECK_IN = "check-in"
    THANK_YOU = "thank-you"
    CUSTOM = "custom"


class EmailTone(str, Enum):
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    CONCISE = "concise"
    PERSUASIVE = "persuasive"


class EmailGenerateRequest(BaseModel):
    lead_id: UUID
    purpose: EmailPurpose = EmailPurpose.FOLLOW_UP
    context: Optional[str] = Field(default="", max_length=1000)
    tone: EmailTone = EmailTone.PROFESSIONAL


class EmailGenerateResponse(BaseModel):
    subject: str
    body: str
    ai_available: bool = True
    source: Optional[str] = None