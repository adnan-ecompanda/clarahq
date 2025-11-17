from pydantic import BaseModel
from typing import Optional

class ProblemBase(BaseModel):
    patient_id: int
    description: str
    icd10_code: Optional[str] = None
    snomed_code: Optional[str] = None
    onset_date: Optional[str] = None
    resolved_date: Optional[str] = None
    chronic: Optional[int] = 0
    status: Optional[str] = "active"  # active / resolved / inactive
    encounter_id: Optional[int] = None
    provider_id: Optional[int] = None
    notes: Optional[str] = None
    active: Optional[int] = 1


class ProblemCreate(ProblemBase):
    pass


class ProblemUpdate(BaseModel):
    description: Optional[str] = None
    icd10_code: Optional[str] = None
    snomed_code: Optional[str] = None
    onset_date: Optional[str] = None
    resolved_date: Optional[str] = None
    chronic: Optional[int] = None
    status: Optional[str] = None
    encounter_id: Optional[int] = None
    provider_id: Optional[int] = None
    notes: Optional[str] = None
    active: Optional[int] = None


class ProblemOut(ProblemBase):
    id: int