from datetime import date
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class LineItem(BaseModel):
    description: str
    quantity: float = 1.0
    price: float = 0.0


class InvoiceBase(BaseModel):
    client_id: str
    project_id: Optional[str] = None
    due_date: date
    line_items: list[LineItem] = []
    currency: str = "usd"


class InvoiceCreate(InvoiceBase):
    pass


class InvoiceUpdate(BaseModel):
    due_date: Optional[date] = None
    line_items: Optional[list[LineItem]] = None
    status: Optional[str] = None
    currency: Optional[str] = None


class InvoiceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    number: str
    client_id: str
    project_id: Optional[str] = None
    status: str
    amount: float
    currency: str
    issue_date: date
    due_date: date
    paid_at: Optional[Any] = None
    line_items: list[Any]
