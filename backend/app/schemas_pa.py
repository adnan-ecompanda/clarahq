from pydantic import BaseModel

class PriorAuthCreate(BaseModel):
    patient_id: str
    provider_npi: str
    payer_id: str
    procedure_code: str
    diagnosis_code: str
    clinical_notes: str | None = None

class PriorAuthRecord(PriorAuthCreate):
    id: int
    status: str
    request_x12: str | None = None
    response_x12: str | None = None