from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_current_user
from app.models.settings import UserSettings
from app.models.user import User
from app.schemas.settings import UserSettingsOut, UserSettingsUpdate

router = APIRouter(prefix="/settings", tags=["settings"])


async def _ensure_settings(db: AsyncSession, user: User) -> UserSettings:
    settings = await db.scalar(
        select(UserSettings).where(UserSettings.user_id == user.id)
    )
    if not settings:
        settings = UserSettings(user_id=user.id)
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
    return settings


@router.get("", response_model=UserSettingsOut)
async def get_settings(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    s = await _ensure_settings(db, user)
    return UserSettingsOut.model_validate(s)


@router.patch("", response_model=UserSettingsOut)
async def update_settings(
    payload: UserSettingsUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    s = await _ensure_settings(db, user)
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(s, key, value)
    await db.commit()
    await db.refresh(s)
    return UserSettingsOut.model_validate(s)
