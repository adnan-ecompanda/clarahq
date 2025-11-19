from pydantic import BaseModel
from typing import Optional


class EligibilityRequest(BaseModel):
    patient_id: int
    insurance_provider: str
    member_id: str
    dob: Optional[str] = None


class EligibilityResponse(BaseModel):
    status: str
    co_pay: int
    deductible_remaining: int
    out_of_pocket_max: int
    effective_date: str
    expiration_date: str
    plan_type: str