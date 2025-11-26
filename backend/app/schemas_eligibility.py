from pydantic import BaseModel
from typing import Optional

class EligibilityRequest(BaseModel):
    patient_id: str
    insurance_provider: str
    patient_first_name: str
    patient_last_name: str
    patient_dob: str
    member_id: str
    payer_id: str
    provider_npi: str


class EligibilityRecord(BaseModel):
    id: int
    patient_id: str
    insurance_provider: str
    patient_first_name: str
    patient_last_name: str
    patient_dob: str
    member_id: str
    payer_id: str
    provider_npi: str
    request_x12: Optional[str] = None
    response_x12: Optional[str] = None
    status: str
    created_at: str