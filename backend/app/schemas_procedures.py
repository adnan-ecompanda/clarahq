from pydantic import BaseModel
from typing import Optional

class ProcedureBase(BaseModel):
    patient_id: int
    encounter_id: Optional[int] = None
    provider_id: Optional[int] = None

    name: str
    cpt_code: Optional[str] = None
    icd10_pcs: Optional[str] = None
    snomed_code: Optional[str] = None

    procedure_date: Optional[str] = None
    notes: Optional[str] = None
    result: Optional[str] = None

    active: Optional[int] = 1


class ProcedureCreate(ProcedureBase):
    pass


class ProcedureUpdate(BaseModel):
    name: Optional[str] = None
    cpt_code: Optional[str] = None
    icd10_pcs: Optional[str] = None
    snomed_code: Optional[str] = None
    procedure_date: Optional[str] = None
    notes: Optional[str] = None
    result: Optional[str] = None
    provider_id: Optional[int] = None
    encounter_id: Optional[int] = None
    active: Optional[int] = None


class ProcedureOut(ProcedureBase):
    id: int