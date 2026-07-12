from pydantic import BaseModel, ConfigDict

from app.schemas.client import ClientOut
from app.schemas.invoice import InvoiceOut
from app.schemas.project import ProjectOut


class PortalProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    project: Optional[ProjectOut] = None
    invoices: list[InvoiceOut] = []
    client: Optional[ClientOut] = None
