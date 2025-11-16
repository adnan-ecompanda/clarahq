from pydantic import BaseModel
from typing import Optional


class EncounterBase(BaseModel):
    patient_id: int
    provider_id: int

    visit_type: Optional[str] = None
    visit_date: Optional[str] = None

    chief_complaint: Optional[str] = None
    hpi: Optional[str] = None
    objective_exam: Optional[str] = None
    assessment: Optional[str] = None
    plan: Optional[str] = None

    vitals_bp: Optional[str] = None
    vitals_hr: Optional[str] = None
    vitals_temp: Optional[str] = None
    vitals_rr: Optional[str] = None
    vitals_spo2: Optional[str] = None

    cpt_code: Optional[str] = None
    icd10_code: Optional[str] = None

    active: Optional[int] = 1


class EncounterCreate(EncounterBase):
    pass


class EncounterUpdate(BaseModel):
    visit_type: Optional[str] = None
    visit_date: Optional[str] = None
    chief_complaint: Optional[str] = None
    hpi: Optional[str] = None
    objective_exam: Optional[str] = None
    assessment: Optional[str] = None
    plan: Optional[str] = None
    vitals_bp: Optional[str] = None
    vitals_hr: Optional[str] = None
    vitals_temp: Optional[str] = None
    vitals_rr: Optional[str] = None
    vitals_spo2: Optional[str] = None
    cpt_code: Optional[str] = None
    icd10_code: Optional[str] = None
    active: Optional[int] = None


class EncounterOut(EncounterBase):
    id: int