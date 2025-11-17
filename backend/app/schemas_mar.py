from pydantic import BaseModel
from typing import Optional


class MedicationOrderBase(BaseModel):
    patient_id: int
    provider_id: int

    medication_name: str
    dose: str
    route: str
    frequency: str

    start_date: Optional[str] = None
    end_date: Optional[str] = None

    instructions: Optional[str] = None
    status: Optional[str] = "active"  # active, completed, discontinued


class MedicationOrderCreate(MedicationOrderBase):
    pass


class MedicationOrderUpdate(BaseModel):
    medication_name: Optional[str] = None
    dose: Optional[str] = None
    route: Optional[str] = None
    frequency: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    instructions: Optional[str] = None
    status: Optional[str] = None


class MedicationOrderOut(MedicationOrderBase):
    id: int
    active: int
    created_at: str
    updated_at: str


# ----------------------- MAR ENTRY -----------------------

class MARBase(BaseModel):
    order_id: int
    administered_by: int
    administered_at: Optional[str] = None

    dose_given: str
    route: str
    notes: Optional[str] = None

    prn_reason: Optional[str] = None  # Only for PRN meds
    prn_effectiveness: Optional[str] = None


class MARCreate(MARBase):
    pass


class MARUpdate(BaseModel):
    administered_at: Optional[str] = None
    dose_given: Optional[str] = None
    route: Optional[str] = None
    notes: Optional[str] = None
    prn_reason: Optional[str] = None
    prn_effectiveness: Optional[str] = None


class MAROut(MARBase):
    id: int
    created_at: str
    updated_at: str
    active: int