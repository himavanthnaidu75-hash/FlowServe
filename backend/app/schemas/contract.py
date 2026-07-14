from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ContractCreate(BaseModel):
    client_id: str
    project_id: Optional[str] = None
    title: str = Field(..., min_length=1, max_length=300)
    contract_type: str = "service_agreement"
    content: str = ""
    variables: dict = {}
    total_value: float = 0
    payment_terms: Optional[str] = None


class ContractUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None
    content: Optional[str] = None
    variables: Optional[dict] = None
    total_value: Optional[float] = None
    payment_terms: Optional[str] = None


class ContractOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    client_id: str
    project_id: Optional[str] = None
    title: str
    contract_type: str
    status: str
    content: str
    variables: dict
    total_value: float
    payment_terms: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    signed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
