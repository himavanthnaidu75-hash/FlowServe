from typing import Any, Optional

from pydantic import BaseModel


class DashboardStats(BaseModel):
    active_projects: int
    revenue: float
    outstanding: float
    tasks: int
    total_revenue: float = 0.0
    hours_tracked: float = 0.0
    completed_projects: int = 0
    recent_activity: list[dict] = []
    revenue_timeline: list[dict] = []


class RevenuePoint(BaseModel):
    month: str
    revenue: float


class ActivityItem(BaseModel):
    id: str
    action: str
    time: str
    entity: str
