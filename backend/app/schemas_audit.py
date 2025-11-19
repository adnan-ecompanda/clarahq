from pydantic import BaseModel
from datetime import datetime

class AuditLogBase(BaseModel):
    user_id: int | None = None
    entity_type: str
    entity_id: int | None = None
    event: str
    meta: dict | None = None

class AuditLogResponse(AuditLogBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True