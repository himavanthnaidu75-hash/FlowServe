from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    message: str
    notification_type: str
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    is_read: bool
    is_dismissed: bool
    action_url: Optional[str] = None
    action_label: Optional[str] = None
    is_automated: bool
    created_at: datetime
