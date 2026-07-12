from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ClientBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=160)
    email: EmailStr
    phone: Optional[str] = None
    company: Optional[str] = None
    notes: Optional[str] = None


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    notes: Optional[str] = None


class ClientOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    email: EmailStr
    phone: Optional[str] = None
    company: Optional[str] = None
    notes: Optional[str] = None
    total_revenue: float
    last_activity: datetime
    created_at: datetime
