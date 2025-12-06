from pydantic import BaseModel

class InsuranceCardCreate(BaseModel):
    patient_id: int
    payer_name: str | None = None
    plan_name: str | None = None
    member_id: str | None = None
    group_id: str | None = None
    relationship: str | None = None
    effective_date: str | None = None
    expiry_date: str | None = None
    priority: str | None = None
    payer_phone: str | None = None
    payer_address: str | None = None