from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class LeadCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    email: Optional[str] = None
    company: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    source: str = "manual"
    estimated_budget: float = 0
    currency: str = "usd"
    project_type: Optional[str] = None
    urgency: str = "normal"
    tags: list[str] = []
    notes: Optional[str] = None


class LeadUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    company: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    stage: Optional[str] = None
    estimated_budget: Optional[float] = None
    project_type: Optional[str] = None
    urgency: Optional[str] = None
    tags: Optional[list[str]] = None
    notes: Optional[str] = None
    lost_reason: Optional[str] = None


class LeadOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    email: Optional[str] = None
    company: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    source: str
    score: int
    stage: str
    estimated_budget: float
    currency: str
    project_type: Optional[str] = None
    urgency: str
    matched_services: list
    tags: list
    last_contacted_at: Optional[datetime] = None
    contact_count: int
    next_followup_at: Optional[datetime] = None
    converted_client_id: Optional[str] = None
    converted_at: Optional[datetime] = None
    lost_reason: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
