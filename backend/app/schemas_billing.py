from pydantic import BaseModel
from typing import List, Optional


class CPTItem(BaseModel):
    cpt_code: str
    units: int
    amount: float
    modifier: Optional[str] = None
    icd_pointer: Optional[str] = None


class ICDItem(BaseModel):
    icd_code: str
    description: Optional[str] = None


class SuperbillCreate(BaseModel):
    encounter_id: int
    patient_id: int
    provider_id: int
    notes: Optional[str] = ""
    status: Optional[str] = "draft"
    cpt_items: List[CPTItem]
    icd_items: List[ICDItem]


class SuperbillResponse(BaseModel):
    id: int
    encounter_id: int
    patient_id: int
    provider_id: int
    notes: str
    status: str
    cpt_items: List[CPTItem]
    icd_items: List[ICDItem]