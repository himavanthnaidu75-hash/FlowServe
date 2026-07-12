from typing import Optional

from pydantic import BaseModel, ConfigDict


class UserSettingsUpdate(BaseModel):
    company_name: Optional[str] = None
    logo_url: Optional[str] = None
    brand_color: Optional[str] = None
    currency: Optional[str] = None
    timezone: Optional[str] = None
    notifications: Optional[dict] = None


class UserSettingsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    company_name: Optional[str] = None
    logo_url: Optional[str] = None
    brand_color: str
    currency: str
    timezone: str
    notifications: dict
