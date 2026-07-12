from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TimeEntryBase(BaseModel):
    description: str = Field(..., min_length=1, max_length=280)
    project_id: Optional[str] = None
    date: Optional[datetime] = None
    hours: float = Field(..., ge=0, le=24)
    billable: bool = True
    hourly_rate: float = 0.0


class TimeEntryCreate(TimeEntryBase):
    pass


class TimeEntryUpdate(BaseModel):
    description: Optional[str] = None
    project_id: Optional[str] = None
    date: Optional[datetime] = None
    hours: Optional[float] = Field(default=None, ge=0, le=24)
    billable: Optional[bool] = None
    hourly_rate: Optional[float] = None


class TimeEntryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    description: str
    project_id: Optional[str] = None
    date: datetime
    hours: float
    billable: bool
    hourly_rate: float
