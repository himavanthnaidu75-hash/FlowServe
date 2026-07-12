"""Seed script — populate dev DB with a sample user + clients + projects + invoices.

Run with:
    python -m scripts.seed
"""
import asyncio
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import select

from app.core.security import hash_password
from app.database import AsyncSessionLocal
from app.models.client import Client
from app.models.invoice import Invoice
from app.models.project import Project
from app.models.user import User


async def main() -> None:
    async with AsyncSessionLocal() as db:
        demo_email = "demo@flowserve.app"
        existing = await db.scalar(select(User).where(User.email == demo_email))
        if existing:
            print(f"Demo user already exists ({demo_email}). Skipping seed.")
            return

        user = User(
            name="Demo User",
            email=demo_email,
            password_hash=hash_password("password123"),
        )
        db.add(user)
        await db.flush()

        clients = [
            Client(
                user_id=user.id,
                name="Acme Corp",
                email="founder@acme.test",
                phone="+1 415 555 1111",
                company="Acme Corp",
                total_revenue=16400,
            ),
            Client(
                user_id=user.id,
                name="StartupX",
                email="hello@startupx.test",
                phone="+1 415 555 2222",
                company="StartupX",
                total_revenue=12000,
            ),
            Client(
                user_id=user.id,
                name="Blogs Inc",
                email="ops@blogsinco.test",
                company="Blogs Inc",
                total_revenue=1500,
            ),
        ]
        db.add_all(clients)
        await db.flush()

        projects = [
            Project(
                user_id=user.id,
                client_id=clients[0].id,
                name="Website Redesign",
                description="Full redesign of the Acme Corp marketing site.",
                status="in_progress",
                deadline=date.today() + timedelta(days=20),
                amount=4500,
                progress=65,
            ),
            Project(
                user_id=user.id,
                client_id=clients[1].id,
                name="Mobile App MVP",
                status="completed",
                deadline=date.today() - timedelta(days=10),
                amount=12000,
                progress=100,
            ),
            Project(
                user_id=user.id,
                client_id=clients[2].id,
                name="SEO Audit",
                status="draft",
                deadline=date.today() + timedelta(days=40),
                amount=1500,
                progress=10,
            ),
        ]
        db.add_all(projects)
        await db.flush()

        invoices = [
            Invoice(
                user_id=user.id,
                client_id=clients[0].id,
                project_id=projects[0].id,
                number="INV-0001",
                status="pending",
                amount=4500,
                currency="usd",
                issue_date=date.today() - timedelta(days=5),
                due_date=date.today() + timedelta(days=10),
                line_items=[
                    {"description": "Hero section + 5 pages", "quantity": 1, "price": 4500}
                ],
            ),
            Invoice(
                user_id=user.id,
                client_id=clients[1].id,
                project_id=projects[1].id,
                number="INV-0002",
                status="paid",
                amount=12000,
                currency="usd",
                issue_date=date.today() - timedelta(days=40),
                due_date=date.today() - timedelta(days=25),
                paid_at=date.today() - timedelta(days=20),
                line_items=[
                    {"description": "MVP build", "quantity": 1, "price": 12000}
                ],
            ),
            Invoice(
                user_id=user.id,
                client_id=clients[2].id,
                number="INV-0003",
                status="overdue",
                amount=1500,
                currency="usd",
                issue_date=date.today() - timedelta(days=30),
                due_date=date.today() - timedelta(days=15),
                line_items=[
                    {"description": "SEO audit report", "quantity": 1, "price": 1500}
                ],
            ),
        ]
        db.add_all(invoices)

        await db.commit()
        print("Seed complete.")
        print(f"  Login: {demo_email} / password123")


if __name__ == "__main__":
    asyncio.run(main())
