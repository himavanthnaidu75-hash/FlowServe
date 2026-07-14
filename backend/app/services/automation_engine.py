"""
Automation Engine — runs smart automations for freelancers.
Handles: recurring invoices, smart follow-ups, deadline reminders,
scope change detection, revenue forecasting, and client re-engagement.
"""
import asyncio
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.client import Client
from app.models.invoice import Invoice
from app.models.project import Project
from app.models.proposal import Proposal
from app.models.time_entry import TimeEntry
from app.models.lead import Lead
from app.models.activity import Activity
from app.models.notification import Notification


async def run_automations():
    """Master automation runner — called periodically."""
    async with AsyncSessionLocal() as db:
        try:
            await _auto_overdue_invoices(db)
            await _smart_followup_reminders(db)
            await _deadline_warnings(db)
            await _scope_change_detection(db)
            await _client_reengagement(db)
            await _win_probability_alerts(db)
            await _revenue_milestone_notifications(db)
            await _inactive_lead_cleanup(db)
            await db.commit()
        except Exception:
            await db.rollback()


async def _auto_overdue_invoices(db: AsyncSession):
    """Auto-transition pending invoices to overdue when past due date."""
    today = date.today()
    result = await db.execute(
        select(Invoice).where(
            Invoice.status == "pending",
            Invoice.due_date < today,
        )
    )
    overdue = result.scalars().all()
    for inv in overdue:
        inv.status = "overdue"
        # Create notification
        notif = Notification(
            user_id=inv.user_id,
            title=f"Invoice #{inv.number} is overdue",
            message=f"Invoice for ${inv.amount:.2f} was due on {inv.due_date}. Consider sending a reminder.",
            notification_type="alert",
            entity_type="invoice",
            entity_id=inv.id,
            action_url=f"/invoices",
            action_label="View Invoice",
            is_automated=True,
            priority="high",
        )
        db.add(notif)
        # Log activity
        activity = Activity(
            user_id=inv.user_id,
            action="overdue",
            entity_type="invoice",
            entity_id=inv.id,
            entity_name=inv.number,
            title=f"Invoice #{inv.number} marked overdue",
            description=f"Amount: ${inv.amount:.2f}, was due: {inv.due_date}",
            priority="high",
        )
        db.add(activity)


async def _smart_followup_reminders(db: AsyncSession):
    """Intelligent follow-up reminders based on proposal/invoice age."""
    now = datetime.now(timezone.utc)

    # Proposals sent >3 days ago with no response
    stale_proposals = await db.execute(
        select(Proposal).where(
            Proposal.status == "sent",
            Proposal.sent_at.isnot(None),
            Proposal.sent_at < now - timedelta(days=3),
        )
    )
    for prop in stale_proposals.scalars().all():
        days_since = (now - prop.sent_at).days
        notif = Notification(
            user_id=prop.user_id,
            title=f"Follow up on proposal: {prop.title}",
            message=f"This proposal was sent {days_since} days ago with no response. A follow-up could increase acceptance rate by 40%.",
            notification_type="reminder",
            entity_type="proposal",
            entity_id=prop.id,
            action_url=f"/proposals",
            action_label="View Proposal",
            is_automated=True,
            priority="normal",
        )
        db.add(notif)

    # Invoices pending >7 days — payment reminder
    stale_invoices = await db.execute(
        select(Invoice).where(
            Invoice.status == "pending",
            Invoice.created_at < now - timedelta(days=7),
        )
    )
    for inv in stale_invoices.scalars().all():
        notif = Notification(
            user_id=inv.user_id,
            title=f"Payment reminder: Invoice #{inv.number}",
            message=f"This invoice (${inv.amount:.2f}) has been pending for over a week. Consider sending a payment reminder.",
            notification_type="reminder",
            entity_type="invoice",
            entity_id=inv.id,
            action_url=f"/invoices",
            action_label="Send Reminder",
            is_automated=True,
            priority="normal",
        )
        db.add(notif)


async def _deadline_warnings(db: AsyncSession):
    """Warn about projects approaching deadline."""
    today = date.today()
    warning_date = today + timedelta(days=3)

    result = await db.execute(
        select(Project).where(
            Project.status.in_(["draft", "in_progress", "review"]),
            Project.deadline.isnot(None),
            Project.deadline <= warning_date,
            Project.deadline >= today,
        )
    )
    for proj in result.scalars().all():
        days_left = (proj.deadline - today).days
        notif = Notification(
            user_id=proj.user_id,
            title=f"Deadline approaching: {proj.name}",
            message=f"Project deadline is in {days_left} day(s) ({proj.deadline}). Current progress: {proj.progress}%.",
            notification_type="alert",
            entity_type="project",
            entity_id=proj.id,
            action_url=f"/projects",
            action_label="View Project",
            is_automated=True,
            priority="high" if days_left <= 1 else "normal",
        )
        db.add(notif)


async def _scope_change_detection(db: AsyncSession):
    """Detect potential scope changes by monitoring time entry spikes."""
    # Find projects where logged time exceeds estimated amount significantly
    result = await db.execute(
        select(
            Project.id,
            Project.name,
            Project.user_id,
            Project.amount,
            func.coalesce(func.sum(TimeEntry.hours), 0).label("total_hours"),
        )
        .join(TimeEntry, TimeEntry.project_id == Project.id, isouter=True)
        .group_by(Project.id)
        .having(Project.amount > 0)
    )
    for row in result.all():
        # If hours * reasonable rate > project amount, flag scope creep
        estimated_rate = 75  # default rate
        estimated_cost = float(row.total_hours) * estimated_rate
        if estimated_cost > float(row.amount) * 1.2:  # 20% over
            notif = Notification(
                user_id=row.user_id,
                title=f"Scope creep detected: {row.name}",
                message=f"Logged hours ({row.total_hours}h) suggest the project may be exceeding its ${row.amount:.0f} budget. Consider a change order.",
                notification_type="suggestion",
                entity_type="project",
                entity_id=row.id,
                action_url=f"/projects",
                action_label="Review Project",
                is_automated=True,
                priority="high",
            )
            db.add(notif)


async def _client_reengagement(db: AsyncSession):
    """Identify clients who haven't been active — re-engagement opportunity."""
    threshold = datetime.now(timezone.utc) - timedelta(days=60)
    result = await db.execute(
        select(Client).where(
            Client.last_activity < threshold,
            Client.total_revenue > 0,
        )
    )
    for client in result.scalars().all():
        days_inactive = (datetime.now(timezone.utc) - client.last_activity).days
        notif = Notification(
            user_id=client.user_id,
            title=f"Re-engage client: {client.name}",
            message=f"{client.name} hasn't been active for {days_inactive} days. They've spent ${client.total_revenue:.0f} — a check-in could lead to repeat business.",
            notification_type="suggestion",
            entity_type="client",
            entity_id=client.id,
            action_url=f"/clients",
            action_label="View Client",
            is_automated=True,
            priority="normal",
        )
        db.add(notif)


async def _win_probability_alerts(db: AsyncSession):
    """Alert about proposals at risk of being lost."""
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(Proposal).where(
            Proposal.status == "sent",
            Proposal.sent_at.isnot(None),
            Proposal.sent_at < now - timedelta(days=14),
        )
    )
    for prop in result.scalars().all():
        days_since = (now - prop.sent_at).days
        notif = Notification(
            user_id=prop.user_id,
            title=f"Proposal at risk: {prop.title}",
            message=f"This proposal (${prop.amount:.0f}) has been pending for {days_since} days. Win probability drops significantly after 2 weeks.",
            notification_type="alert",
            entity_type="proposal",
            entity_id=prop.id,
            action_url=f"/proposals",
            action_label="Follow Up",
            is_automated=True,
            priority="high",
        )
        db.add(notif)


async def _revenue_milestone_notifications(db: AsyncSession):
    """Celebrate revenue milestones."""
    result = await db.execute(
        select(
            Client.user_id,
            func.coalesce(func.sum(Invoice.amount), 0).label("total"),
        )
        .where(Invoice.status == "paid")
        .group_by(Client.user_id)
    )
    for row in result.all():
        total = float(row.total)
        milestones = [1000, 5000, 10000, 25000, 50000, 100000]
        for m in milestones:
            if total >= m:
                # Check if we already notified for this milestone
                existing = await db.execute(
                    select(Notification).where(
                        Notification.user_id == row.user_id,
                        Notification.title.contains(f"${m:,}"),
                    ).limit(1)
                )
                if not existing.scalar_one_or_none():
                    notif = Notification(
                        user_id=row.user_id,
                        title=f"Revenue milestone: ${m:,}!",
                        message=f"Congratulations! You've earned ${total:,.0f} in total revenue. Keep up the great work!",
                        notification_type="achievement",
                        is_automated=True,
                        priority="normal",
                    )
                    db.add(notif)


async def _inactive_lead_cleanup(db: AsyncSession):
    """Move stale leads to 'lost' stage."""
    threshold = datetime.now(timezone.utc) - timedelta(days=30)
    result = await db.execute(
        select(Lead).where(
            Lead.stage.in_(["new", "contacted"]),
            Lead.updated_at < threshold,
        )
    )
    for lead in result.scalars().all():
        lead.stage = "lost"
        lead.lost_reason = "Auto-closed: no activity for 30 days"
