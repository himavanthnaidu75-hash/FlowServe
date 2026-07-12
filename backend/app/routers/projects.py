from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.deps import get_current_user
from app.models.client import Client
from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectOut, ProjectStatusUpdate, ProjectUpdate

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[ProjectOut])
async def list_projects(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    status: str | None = None,
):
    stmt = (
        select(Project)
        .where(Project.user_id == user.id)
        .options(selectinload(Project.client))
        .order_by(Project.created_at.desc())
    )
    if status:
        stmt = stmt.where(Project.status == status)

    result = await db.execute(stmt)
    projects = result.scalars().all()
    return [ProjectOut.model_validate(p) for p in projects]


@router.post("", response_model=ProjectOut, status_code=201)
async def create_project(
    payload: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    client = await db.scalar(
        select(Client).where(Client.id == payload.client_id, Client.user_id == user.id)
    )
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    project = Project(
        user_id=user.id,
        client_id=payload.client_id,
        name=payload.name,
        description=payload.description,
        deadline=payload.deadline,
        amount=payload.amount,
        progress=payload.progress,
        status=payload.status or "draft",
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)

    # Load the client relation for the response
    await db.refresh(project, attribute_names=["client"])
    return ProjectOut.model_validate(project)


@router.get("/{project_id}", response_model=ProjectOut)
async def get_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    project = await db.scalar(
        select(Project)
        .where(Project.id == project_id, Project.user_id == user.id)
        .options(selectinload(Project.client))
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectOut.model_validate(project)


@router.patch("/{project_id}", response_model=ProjectOut)
async def update_project(
    project_id: str,
    payload: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    project = await db.scalar(
        select(Project)
        .where(Project.id == project_id, Project.user_id == user.id)
        .options(selectinload(Project.client))
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    data = payload.model_dump(exclude_unset=True)

    if "client_id" in data and data["client_id"]:
        client = await db.scalar(
            select(Client).where(Client.id == data["client_id"], Client.user_id == user.id)
        )
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")

    for key, value in data.items():
        setattr(project, key, value)

    await db.commit()
    await db.refresh(project)
    return ProjectOut.model_validate(project)


@router.patch("/{project_id}/status", response_model=ProjectOut)
async def update_project_status(
    project_id: str,
    payload: ProjectStatusUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    project = await db.scalar(
        select(Project)
        .where(Project.id == project_id, Project.user_id == user.id)
        .options(selectinload(Project.client))
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project.status = payload.status
    if payload.status == "completed":
        project.progress = 100

    await db.commit()
    await db.refresh(project)
    return ProjectOut.model_validate(project)


@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    project = await db.scalar(
        select(Project).where(Project.id == project_id, Project.user_id == user.id)
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    await db.delete(project)
    await db.commit()
    return None
