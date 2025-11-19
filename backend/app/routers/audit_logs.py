from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.schemas_audit import AuditLogResponse, AuditLogBase
from app.crud.crud_audit import get_audit_logs

router = APIRouter(prefix="/audit", tags=["Audit Logs"])

@router.get("/", response_model=list[AuditLogResponse])
def list_logs(
    entity_type: str | None = None,
    entity_id: int | None = None,
    user_id: int | None = None,
    event: str | None = None,
    db: Session = Depends(get_db)
):
    filters = AuditLogBase(
        entity_type=entity_type,
        entity_id=entity_id,
        user_id=user_id,
        event=event,
    )
    return get_audit_logs(db, filters)