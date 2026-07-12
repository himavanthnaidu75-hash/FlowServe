from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.client import ClientOut


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=220)
    description: Optional[str] = None
    client_id: str
    deadline: Optional[date] = None
    amount: float = 0.0
    progress: int = 0


class ProjectCreate(ProjectBase):
    status: Optional[str] = "draft"


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    client_id: Optional[str] = None
    deadline: Optional[date] = None
    amount: Optional[float] = None
    progress: Optional[int] = Field(None, ge=0, le=100)
    status: Optional[str] = Field(None, pattern="^(draft|in_progress|review|completed)$")


class ProjectStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(draft|in_progress|review|completed)$")


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: Optional[str] = None
    client: Optional[ClientOut] = None
    client_id: str
    status: str
    deadline: Optional[date] = None
    amount: float
    progress: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
