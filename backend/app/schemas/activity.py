from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ActivityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    action: str
    entity_type: str
    entity_id: str
    entity_name: Optional[str] = None
    title: str
    description: Optional[str] = None
    priority: str
    created_at: datetime
