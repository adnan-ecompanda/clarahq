from pydantic import BaseModel
from typing import List, Optional


class ClaimLine(BaseModel):
    cpt_code: str
    units: int
    amount: float
    modifier: Optional[str] = None
    icd_pointer: Optional[str] = None


class ClaimResponse(BaseModel):
    id: int
    superbill_id: int
    patient_id: int
    provider_id: int
    status: str
    lines: List[ClaimLine]