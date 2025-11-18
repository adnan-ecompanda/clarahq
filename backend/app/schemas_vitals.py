from pydantic import BaseModel
from typing import Optional


class VitalsCreate(BaseModel):
    patient_id: int
    encounter_id: Optional[int] = None
    taken_by: int

    bp_systolic: Optional[int] = None
    bp_diastolic: Optional[int] = None
    heart_rate: Optional[int] = None
    respiratory_rate: Optional[int] = None
    temperature: Optional[float] = None
    spo2: Optional[int] = None
    weight: Optional[float] = None
    height: Optional[float] = None

    notes: Optional[str] = None


class FlowsheetRowCreate(VitalsCreate):
    panel: str