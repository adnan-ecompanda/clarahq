from sqlalchemy.orm import Session
from app.schemas.schemas_audit import AuditLogBase
from app.crud.crud_audit import create_audit_log

def log_event(
    db: Session,
    *,
    user_id=None,
    entity_type="",
    entity_id=None,
    event="",
    meta=None
):
    log = AuditLogBase(
        user_id=user_id,
        entity_type=entity_type,
        entity_id=entity_id,
        event=event,
        meta=meta or {}
    )
    create_audit_log(db, log)