from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_current_user
from app.models.project import Project
from app.models.time_entry import TimeEntry
from app.models.user import User
from app.schemas.time_entry import TimeEntryCreate, TimeEntryOut, TimeEntryUpdate

router = APIRouter(prefix="/time-entries", tags=["time-entries"])


@router.get("", response_model=list[TimeEntryOut])
async def list_entries(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    project_id: str | None = None,
):
    stmt = select(TimeEntry).where(TimeEntry.user_id == user.id)
    if project_id:
        stmt = stmt.where(TimeEntry.project_id == project_id)
    stmt = stmt.order_by(TimeEntry.date.desc())
    result = await db.execute(stmt)
    return [TimeEntryOut.model_validate(t) for t in result.scalars().all()]


@router.post("", response_model=TimeEntryOut, status_code=201)
async def create_entry(
    payload: TimeEntryCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if payload.project_id:
        project = await db.scalar(
            select(Project).where(
                Project.id == payload.project_id, Project.user_id == user.id
            )
        )
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

    entry = TimeEntry(
        user_id=user.id,
        project_id=payload.project_id,
        description=payload.description,
        date=payload.date or datetime.now(timezone.utc),
        hours=float(payload.hours),
        billable=payload.billable,
        hourly_rate=float(payload.hourly_rate),
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return TimeEntryOut.model_validate(entry)


@router.get("/{entry_id}", response_model=TimeEntryOut)
async def get_entry(
    entry_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    entry = await db.scalar(
        select(TimeEntry).where(
            TimeEntry.id == entry_id, TimeEntry.user_id == user.id
        )
    )
    if not entry:
        raise HTTPException(status_code=404, detail="Time entry not found")
    return TimeEntryOut.model_validate(entry)


@router.patch("/{entry_id}", response_model=TimeEntryOut)
async def update_entry(
    entry_id: str,
    payload: TimeEntryUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    entry = await db.scalar(
        select(TimeEntry).where(
            TimeEntry.id == entry_id, TimeEntry.user_id == user.id
        )
    )
    if not entry:
        raise HTTPException(status_code=404, detail="Time entry not found")

    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(entry, key, value)

    await db.commit()
    await db.refresh(entry)
    return TimeEntryOut.model_validate(entry)


@router.delete("/{entry_id}", status_code=204)
async def delete_entry(
    entry_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    entry = await db.scalar(
        select(TimeEntry).where(
            TimeEntry.id == entry_id, TimeEntry.user_id == user.id
        )
    )
    if not entry:
        raise HTTPException(status_code=404, detail="Time entry not found")
    await db.delete(entry)
    await db.commit()
    return None
