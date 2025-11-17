from pydantic import BaseModel
from typing import Optional

class MedicationBase(BaseModel):
    patient_id: int
    provider_id: int
    encounter_id: Optional[int] = None

    medication_name: str
    strength: Optional[str] = None
    route: Optional[str] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None
    quantity: Optional[str] = None
    refills: Optional[int] = 0
    instructions: Optional[str] = None

    allergy_checked: Optional[int] = 0
    drug_interaction_checked: Optional[int] = 0

    status: Optional[str] = "active"
    approved_by: Optional[int] = None
    approved_at: Optional[str] = None
    active: Optional[int] = 1


class MedicationCreate(MedicationBase):
    pass


class MedicationUpdate(BaseModel):
    medication_name: Optional[str] = None
    strength: Optional[str] = None
    route: Optional[str] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None
    quantity: Optional[str] = None
    refills: Optional[int] = None
    instructions: Optional[str] = None
    allergy_checked: Optional[int] = None
    drug_interaction_checked: Optional[int] = None
    status: Optional[str] = None
    approved_by: Optional[int] = None
    approved_at: Optional[str] = None
    active: Optional[int] = None


class MedicationOut(MedicationBase):
    id: int