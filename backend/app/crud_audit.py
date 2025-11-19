from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog
from app.schemas.schemas_audit import AuditLogBase

def create_audit_log(db: Session, log: AuditLogBase):
    db_log = AuditLog(
        user_id=log.user_id,
        entity_type=log.entity_type,
        entity_id=log.entity_id,
        event=log.event,
        meta=log.meta or {}
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def get_audit_logs(db: Session, filters):
    query = db.query(AuditLog)

    if filters.entity_type:
        query = query.filter(AuditLog.entity_type == filters.entity_type)

    if filters.entity_id:
        query = query.filter(AuditLog.entity_id == filters.entity_id)

    if filters.user_id:
        query = query.filter(AuditLog.user_id == filters.user_id)

    if filters.event:
        query = query.filter(AuditLog.event == filters.event)

    return query.order_by(AuditLog.timestamp.desc()).all()