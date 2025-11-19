from pydantic import BaseModel
from typing import Optional


class PrescriptionCreate(BaseModel):
    patient_id: int
    provider_id: int
    medication_name: str
    dose: str
    route: Optional[str] = None
    frequency: Optional[str] = None
    quantity: Optional[str] = None
    refills: Optional[int] = 0
    instructions: Optional[str] = None
    diagnosis: Optional[str] = None


class PrescriptionOut(PrescriptionCreate):
    id: int