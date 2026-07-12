from datetime import date
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class ProposalSection(BaseModel):
    type: str = Field(..., description="overview | timeline | pricing | terms | custom")
    title: str
    content: Any = None


class ProposalBase(BaseModel):
    title: str
    client_id: str
    amount: float = 0.0
    date: Optional[date] = None
    sections: list[ProposalSection] = []
    status: Optional[str] = "draft"


class ProposalCreate(ProposalBase):
    pass


class ProposalUpdate(BaseModel):
    title: Optional[str] = None
    client_id: Optional[str] = None
    amount: Optional[float] = None
    date: Optional[date] = None
    sections: Optional[list[ProposalSection]] = None
    status: Optional[str] = None


class ProposalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    client_id: str
    status: str
    amount: float
    date: date
    sent_at: Optional[Any] = None
    sections: list[Any]
