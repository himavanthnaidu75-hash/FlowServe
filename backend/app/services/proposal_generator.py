"""
Smart Proposal Generator — creates professional proposals based on
project briefs, client data, and historical patterns.
"""
from datetime import datetime, timezone
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.models.client import Client
from app.models.invoice import Invoice
from app.models.proposal import Proposal
from app.models.time_entry import TimeEntry


async def generate_proposal_draft(
    db: AsyncSession,
    user_id: str,
    client_id: str,
    project_brief: str,
    budget_hint: float = 0,
) -> dict:
    """Generate a smart proposal draft based on context."""

    # Get client history
    client = await db.scalar(select(Client).where(Client.id == client_id))
    client_history = await _get_client_history(db, client_id)

    # Get user's typical patterns
    user_patterns = await _get_user_patterns(db, user_id)

    # Estimate pricing
    suggested_price = _estimate_price(user_patterns, budget_hint, project_brief)

    # Generate sections
    sections = _generate_sections(
        project_brief=project_brief,
        client_name=client.name if client else "Client",
        client_history=client_history,
        suggested_price=suggested_price,
        user_patterns=user_patterns,
    )

    # Estimate timeline
    estimated_days = _estimate_timeline(suggested_price, user_patterns)

    return {
        "title": _generate_title(project_brief),
        "sections": sections,
        "suggested_amount": suggested_price,
        "estimated_timeline_days": estimated_days,
        "confidence": _calculate_confidence(user_patterns, client_history),
        "tips": _generate_tips(client_history, user_patterns),
    }


async def _get_client_history(db: AsyncSession, client_id: str) -> dict:
    """Get historical data about this client."""
    # Total spent
    total = await db.execute(
        select(func.coalesce(func.sum(Invoice.amount), 0)).where(
            Invoice.client_id == client_id,
            Invoice.status == "paid",
        )
    )
    total_spent = float(total.scalar() or 0)

    # Project count
    projects = await db.execute(
        select(func.count(Project.id)).where(Project.client_id == client_id)
    )
    project_count = projects.scalar() or 0

    # Average project value
    avg = total_spent / project_count if project_count > 0 else 0

    # Payment reliability (average days to pay)
    paid_invoices = await db.execute(
        select(Invoice).where(
            Invoice.client_id == client_id,
            Invoice.status == "paid",
            Invoice.paid_at.isnot(None),
        )
    )
    avg_days_to_pay = 0
    invoices = paid_invoices.scalars().all()
    if invoices:
        days_list = []
        for inv in invoices:
            if inv.paid_at and inv.issue_date:
                days = (inv.paid_at.date() - inv.issue_date).days
                days_list.append(days)
        avg_days_to_pay = sum(days_list) / len(days_list) if days_list else 0

    return {
        "total_spent": total_spent,
        "project_count": project_count,
        "avg_project_value": avg,
        "avg_days_to_pay": avg_days_to_pay,
        "is_returning": project_count > 0,
    }


async def _get_user_patterns(db: AsyncSession, user_id: str) -> dict:
    """Get freelancer's typical patterns."""
    # Average hourly rate
    rate = await db.execute(
        select(func.avg(TimeEntry.hourly_rate)).where(
            TimeEntry.user_id == user_id,
            TimeEntry.hourly_rate > 0,
        )
    )
    avg_rate = float(rate.scalar() or 75)

    # Average project value
    avg_val = await db.execute(
        select(func.avg(Project.amount)).where(
            Project.user_id == user_id,
            Project.amount > 0,
        )
    )
    avg_project_value = float(avg_val.scalar() or 2500)

    # Average project duration
    result = await db.execute(
        select(Project.created_at, Project.deadline).where(
            Project.user_id == user_id,
            Project.deadline.isnot(None),
        )
    )
    durations = []
    for row in result.all():
        if row[0] and row[1]:
            days = (row[1] - row[0].date()).days
            if 0 < days < 365:
                durations.append(days)
    avg_duration = sum(durations) / len(durations) if durations else 30

    return {
        "avg_rate": avg_rate,
        "avg_project_value": avg_project_value,
        "avg_duration_days": avg_duration,
    }


def _estimate_price(patterns: dict, budget_hint: float, brief: str) -> float:
    """Estimate appropriate price for the project."""
    if budget_hint > 0:
        return budget_hint

    base = patterns.get("avg_project_value", 2500)

    # Adjust based on brief complexity keywords
    complex_keywords = ["complex", "enterprise", "integration", "api", "database", "security", "scale"]
    simple_keywords = ["simple", "landing", "basic", "small", "quick"]

    brief_lower = brief.lower()
    complexity_factor = 1.0
    for kw in complex_keywords:
        if kw in brief_lower:
            complexity_factor += 0.2
    for kw in simple_keywords:
        if kw in brief_lower:
            complexity_factor -= 0.15

    return round(base * max(0.5, min(complexity_factor, 2.5)), 2)


def _generate_title(brief: str) -> str:
    """Generate a professional proposal title from the brief."""
    words = brief.strip().split()[:8]
    title = " ".join(words)
    if not title.endswith(("Project", "Proposal", "Solution")):
        title += " — Project Proposal"
    return title


def _generate_sections(brief, client_name, client_history, suggested_price, user_patterns) -> list:
    """Generate proposal sections."""
    sections = []

    # Overview
    sections.append({
        "type": "overview",
        "title": "Project Overview",
        "content": (
            f"Thank you for considering us for this project, {client_name}. "
            f"Based on our understanding of your requirements, we're confident we can "
            f"deliver exceptional results.\n\n"
            f"**Project Scope:** {brief}\n\n"
            f"{'As a returning client, we\'re pleased to offer our preferred partner rates.' if client_history.get('is_returning') else ''}"
        ),
    })

    # Approach
    sections.append({
        "type": "overview",
        "title": "Our Approach",
        "content": (
            "We follow a structured, agile methodology:\n\n"
            "1. **Discovery & Planning** — Deep dive into requirements, timeline, and success criteria\n"
            "2. **Design & Prototyping** — Iterative design with your feedback at each stage\n"
            "3. **Development & Testing** — Rigorous development with continuous integration\n"
            "4. **Launch & Support** — Smooth deployment with post-launch support included"
        ),
    })

    # Timeline
    sections.append({
        "type": "timeline",
        "title": "Timeline & Milestones",
        "content": (
            "Estimated timeline: 2-4 weeks\n\n"
            "**Week 1:** Discovery, planning, and initial design\n"
            "**Week 2:** Core development and integration\n"
            "**Week 3:** Testing, refinement, and client review\n"
            "**Week 4:** Final delivery and launch support"
        ),
    })

    # Pricing
    sections.append({
        "type": "pricing",
        "title": "Investment",
        "content": (
            f"**Total Investment:** ${suggested_price:,.0f}\n\n"
            "This includes:\n"
            "- Full project scope as outlined above\n"
            "- Up to 2 rounds of revisions\n"
            "- 30 days of post-launch support\n"
            "- Source files and documentation\n\n"
            "**Payment Terms:** 50% upfront, 50% upon completion"
        ),
    })

    # Terms
    sections.append({
        "type": "terms",
        "title": "Terms & Conditions",
        "content": (
            "- Work begins upon receipt of signed proposal and initial payment\n"
            "- Intellectual property transfers upon full payment\n"
            "- Confidentiality guaranteed for all project materials\n"
            "- Additional scope changes quoted separately\n"
            "- 30-day warranty on all deliverables"
        ),
    })

    return sections


def _estimate_timeline(price: float, patterns: dict) -> int:
    """Estimate project timeline in days."""
    base = patterns.get("avg_duration_days", 21)
    # Scale by price relative to average
    avg = patterns.get("avg_project_value", 2500)
    if avg > 0:
        ratio = price / avg
        return max(7, int(base * min(ratio, 2.0)))
    return base


def _calculate_confidence(patterns: dict, client_history: dict) -> float:
    """Calculate confidence score for the proposal."""
    confidence = 0.5  # Base

    if patterns["avg_project_value"] > 0:
        confidence += 0.15
    if client_history.get("is_returning"):
        confidence += 0.2
    if client_history.get("avg_days_to_pay", 30) < 15:
        confidence += 0.1
    if patterns["avg_rate"] > 50:
        confidence += 0.05

    return min(confidence, 0.95)


def _generate_tips(client_history: dict, patterns: dict) -> list:
    """Generate smart tips for closing the deal."""
    tips = []

    if client_history.get("is_returning"):
        tips.append("This is a returning client — mention your previous successful work together.")

    if client_history.get("avg_days_to_pay", 30) > 20:
        tips.append("This client pays slowly — consider requiring larger upfront payment.")

    if client_history.get("total_spent", 0) > 5000:
        tips.append("High-value client — consider offering a loyalty discount for future projects.")

    if not client_history.get("is_returning"):
        tips.append("New client — include social proof and case studies to build trust.")

    tips.append("Follow up within 3 days if no response — proposals sent within 24h have 40% higher acceptance.")

    return tips
