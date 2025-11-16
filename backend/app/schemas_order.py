from pydantic import BaseModel
from typing import Optional


class OrderCreate(BaseModel):
    patient_id: int
    encounter_id: Optional[int] = None
    provider_id: int

    order_type: str  # lab, imaging, medication
    name: str
    details: Optional[str] = None
    priority: Optional[str] = "routine"
    clinical_notes: Optional[str] = None

    external_order_id: Optional[str] = None
    external_location: Optional[str] = None


class OrderUpdate(BaseModel):
    details: Optional[str] = None
    priority: Optional[str] = None
    clinical_notes: Optional[str] = None
    status: Optional[str] = None
    external_order_id: Optional[str] = None
    external_location: Optional[str] = None
    active: Optional[int] = None


class OrderOut(BaseModel):
    id: int
    patient_id: int
    encounter_id: Optional[int]
    provider_id: int

    order_type: str
    name: str
    details: Optional[str]
    priority: Optional[str]
    clinical_notes: Optional[str]
    status: str
    external_order_id: Optional[str]
    external_location: Optional[str]

    created_at: str
    updated_at: str
    active: int