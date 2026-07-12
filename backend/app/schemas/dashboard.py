from typing import Any

from pydantic import BaseModel


class DashboardStats(BaseModel):
    active_projects: int
    revenue: float
    outstanding: float
    tasks: int


class RevenuePoint(BaseModel):
    month: str
    revenue: float


class ActivityItem(BaseModel):
    id: str
    action: str
    time: str
    entity: str
