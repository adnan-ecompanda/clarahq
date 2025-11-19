from sqlalchemy import Column, Integer, String, DateTime, JSON, func
from app.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)

    entity_type = Column(String(100), nullable=False)
    entity_id = Column(Integer, nullable=True)

    event = Column(String(50), nullable=False)  # created, updated, deleted

    meta = Column(JSON, nullable=True)

    timestamp = Column(DateTime(timezone=True), server_default=func.now())