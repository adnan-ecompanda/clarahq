from pydantic import BaseModel
from typing import Optional


class ReferralCreate(BaseModel):
    patient_id: int
    encounter_id: Optional[int] = None
    provider_id: int
    referral_type: Optional[str] = None
    referred_to: Optional[str] = None
    specialty: Optional[str] = None
    reason: Optional[str] = None
    clinical_summary: Optional[str] = None


class ReferralStatusUpdate(BaseModel):
    status: str
    note: Optional[str] = None