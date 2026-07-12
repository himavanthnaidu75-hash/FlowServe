import asyncio
from datetime import datetime, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.integrations import create_payment_link, send_email
from app.database import get_db
from app.deps import get_current_user
from app.models.client import Client
from app.models.invoice import Invoice
from app.models.user import User
from app.schemas.invoice import InvoiceCreate, InvoiceOut, InvoiceUpdate

router = APIRouter(prefix="/invoices", tags=["invoices"])


def _serialize(inv: Invoice) -> dict:
    return {
        "id": inv.id,
        "number": inv.number,
        "client_id": inv.client_id,
        "project_id": inv.project_id,
        "status": inv.status,
        "amount": float(inv.amount or 0),
        "currency": inv.currency,
        "issue_date": inv.issue_date,
        "due_date": inv.due_date,
        "paid_at": inv.paid_at,
        "line_items": inv.line_items or [],
    }


async def _gen_invoice_number(db: AsyncSession, user_id: str) -> str:
    count = await db.scalar(
        select(func.count(Invoice.id)).where(Invoice.user_id == user_id)
    )
    return f"INV-{int(count or 0) + 1:04d}"


@router.get("", response_model=list[InvoiceOut])
async def list_invoices(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    status: str | None = None,
):
    stmt = select(Invoice).where(Invoice.user_id == user.id)
    if status:
        stmt = stmt.where(Invoice.status == status)
    stmt = stmt.order_by(Invoice.created_at.desc())
    result = await db.execute(stmt)
    return [InvoiceOut.model_validate(_serialize(i)) for i in result.scalars().all()]


@router.post("", response_model=InvoiceOut, status_code=201)
async def create_invoice(
    payload: InvoiceCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    client = await db.scalar(
        select(Client).where(Client.id == payload.client_id, Client.user_id == user.id)
    )
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    total = sum(
        Decimal(str(li.quantity)) * Decimal(str(li.unit_price)) for li in payload.line_items
    )
    number = await _gen_invoice_number(db, user.id)

    invoice = Invoice(
        user_id=user.id,
        client_id=payload.client_id,
        project_id=payload.project_id,
        number=number,
        amount=float(total),
        currency=payload.currency,
        due_date=payload.due_date,
        line_items=[li.model_dump() for li in payload.line_items],
        status="pending",
    )
    db.add(invoice)
    await db.commit()
    await db.refresh(invoice)
    return InvoiceOut.model_validate(_serialize(invoice))


@router.get("/{invoice_id}", response_model=InvoiceOut)
async def get_invoice(
    invoice_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    inv = await db.scalar(
        select(Invoice).where(Invoice.id == invoice_id, Invoice.user_id == user.id)
    )
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return InvoiceOut.model_validate(_serialize(inv))


@router.patch("/{invoice_id}", response_model=InvoiceOut)
async def update_invoice(
    invoice_id: str,
    payload: InvoiceUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    inv = await db.scalar(
        select(Invoice).where(Invoice.id == invoice_id, Invoice.user_id == user.id)
    )
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")

    data = payload.model_dump(exclude_unset=True)
    if payload.line_items is not None:
        inv.line_items = [li.model_dump() for li in payload.line_items]
        inv.amount = float(
            sum(Decimal(str(li.quantity)) * Decimal(str(li.unit_price)) for li in payload.line_items)
        )

    if payload.due_date is not None:
        inv.due_date = payload.due_date
    if payload.currency is not None:
        inv.currency = payload.currency
    if payload.status is not None:
        inv.status = payload.status
        if payload.status == "paid":
            inv.paid_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(inv)
    return InvoiceOut.model_validate(_serialize(inv))


@router.post("/{invoice_id}/pay", response_model=InvoiceOut)
async def pay_invoice(
    invoice_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    inv = await db.scalar(
        select(Invoice)
        .where(Invoice.id == invoice_id, Invoice.user_id == user.id)
        .options(selectinload(Invoice.client))
    )
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    if inv.status == "paid":
        raise HTTPException(status_code=400, detail="Invoice already paid")

    inv.status = "paid"
    inv.paid_at = datetime.now(timezone.utc)

    # bump client total revenue
    inv.client.total_revenue = float(inv.client.total_revenue or 0) + float(inv.amount or 0)
    inv.client.last_activity = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(inv)
    return InvoiceOut.model_validate(_serialize(inv))


@router.delete("/{invoice_id}", status_code=204)
async def delete_invoice(
    invoice_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    inv = await db.scalar(
        select(Invoice).where(Invoice.id == invoice_id, Invoice.user_id == user.id)
    )
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")

    await db.delete(inv)
    await db.commit()


@router.post("/{invoice_id}/remind")
async def remind_invoice(
    invoice_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    inv = await db.scalar(
        select(Invoice)
        .where(Invoice.id == invoice_id, Invoice.user_id == user.id)
        .options(selectinload(Invoice.client))
    )
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    if inv.status == "paid":
        raise HTTPException(status_code=400, detail="Invoice already paid")

    loop = asyncio.get_running_loop()
    pay_url = await loop.run_in_executor(None, create_payment_link, inv.number, float(inv.amount or 0), inv.currency)
    html = (
        f"<p>Hi {inv.client.name},</p>"
        f"<p>This is a friendly reminder that invoice <b>{inv.number}</b> "
        f"for ${inv.amount:.2f} is due on {inv.due_date}.</p>"
        f"<p><a href='{pay_url}'>Pay invoice</a></p>"
        f"<p>— {user.name}</p>"
    )
    dispatched = await loop.run_in_executor(None, send_email, inv.client.email, f"Reminder: invoice {inv.number}", html)
    return {"sent": dispatched, "invoice_id": inv.id, "number": inv.number}
