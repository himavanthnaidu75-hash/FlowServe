"""
Lead Scoring Engine — intelligently scores and ranks leads based on
multiple signals: budget, urgency, fit, engagement, and conversion potential.
"""
from datetime import datetime, timezone
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lead import Lead
from app.models.client import Client
from app.models.project import Project
from app.models.invoice import Invoice


def score_lead(lead: Lead, user_history: dict = None) -> int:
    """
    Score a lead 0-100 based on multiple factors:
    - Budget fit (0-25 points)
    - Urgency (0-20 points)
    - Engagement signals (0-20 points)
    - Profile completeness (0-15 points)
    - Historical conversion fit (0-20 points)
    """
    score = 0
    user_history = user_history or {}

    # Budget fit (0-25)
    budget = float(lead.estimated_budget or 0)
    if budget >= 10000:
        score += 25
    elif budget >= 5000:
        score += 20
    elif budget >= 1000:
        score += 15
    elif budget >= 500:
        score += 10
    elif budget > 0:
        score += 5

    # Urgency (0-20)
    urgency_scores = {"urgent": 20, "high": 15, "normal": 10, "low": 5}
    score += urgency_scores.get(lead.urgency, 10)

    # Engagement (0-20)
    if lead.contact_count > 3:
        score += 20
    elif lead.contact_count > 1:
        score += 15
    elif lead.contact_count == 1:
        score += 10

    if lead.email:
        score += 5
    if lead.phone:
        score += 5

    # Profile completeness (0-15)
    completeness = 0
    if lead.name:
        completeness += 3
    if lead.email:
        completeness += 3
    if lead.company:
        completeness += 3
    if lead.website:
        completeness += 3
    if lead.description and len(lead.description) > 20:
        completeness += 3
    score += min(completeness, 15)

    # Historical conversion fit (0-20)
    if user_history.get("avg_project_value", 0) > 0:
        ratio = budget / user_history["avg_project_value"] if budget > 0 else 0
        if 0.5 <= ratio <= 2.0:
            score += 20  # Perfect fit
        elif 0.2 <= ratio <= 5.0:
            score += 15
        elif ratio > 0:
            score += 10

    if user_history.get("preferred_project_type") and lead.project_type:
        if lead.project_type == user_history["preferred_project_type"]:
            score += 10

    return min(score, 100)


async def calculate_user_history(db: AsyncSession, user_id: str) -> dict:
    """Calculate user's historical patterns for lead scoring."""
    # Average project value
    result = await db.execute(
        select(func.coalesce(func.avg(Project.amount), 0)).where(Project.user_id == user_id)
    )
    avg_project_value = float(result.scalar() or 0)

    # Conversion rate
    total_leads = await db.execute(
        select(func.count(Lead.id)).where(Lead.user_id == user_id)
    )
    won_leads = await db.execute(
        select(func.count(Lead.id)).where(Lead.user_id == user_id, Lead.stage == "won")
    )
    total = total_leads.scalar() or 0
    won = won_leads.scalar() or 0
    conversion_rate = (won / total * 100) if total > 0 else 0

    # Most common project type
    from sqlalchemy import func as sqlfunc
    type_result = await db.execute(
        select(Lead.project_type, sqlfunc.count(Lead.id))
        .where(Lead.user_id == user_id, Lead.project_type.isnot(None))
        .group_by(Lead.project_type)
        .order_by(sqlfunc.count(Lead.id).desc())
        .limit(1)
    )
    preferred_type = type_result.first()
    preferred_project_type = preferred_type[0] if preferred_type else None

    return {
        "avg_project_value": avg_project_value,
        "conversion_rate": conversion_rate,
        "preferred_project_type": preferred_project_type,
        "total_leads": total,
        "won_leads": won,
    }


def suggest_lead_stage(lead: Lead) -> str:
    """Suggest the next best stage for a lead based on signals."""
    if lead.stage == "new":
        if lead.score >= 70:
            return "contacted"  # High value, reach out immediately
        elif lead.score >= 40:
            return "contacted"
        else:
            return "new"  # Nurture

    if lead.stage == "contacted":
        if lead.contact_count >= 2:
            return "qualified"
        elif lead.last_contacted_at and (datetime.now(timezone.utc) - lead.last_contacted_at).days > 7:
            return "qualified"  # Follow up

    return lead.stage


def estimate_deal_value(lead: Lead, user_history: dict = None) -> float:
    """Estimate likely deal value based on lead data and history."""
    budget = float(lead.estimated_budget or 0)
    if budget > 0:
        return budget

    user_history = user_history or {}
    avg = user_history.get("avg_project_value", 2500)

    # Type-based estimates
    type_multipliers = {
        "web_design": 1.2,
        "web_development": 1.5,
        "mobile_app": 2.0,
        "consulting": 0.8,
        "branding": 0.6,
        "marketing": 0.7,
    }
    multiplier = type_multipliers.get(lead.project_type or "", 1.0)

    return avg * multiplier
