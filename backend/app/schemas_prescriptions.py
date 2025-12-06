from pydantic import BaseModel
from typing import Optional


class PrescriptionCreate(BaseModel):
    patient_id: int
    encounter_id: Optional[int] = None
    medication_name: str
    dosage: str
    route: str
    frequency: str
    duration: str
    quantity: str
    refills: int = 0
    instructions: Optional[str] = None


class PrescriptionSign(BaseModel):
    provider_id: int
    signature_base64: str
    signed_at: str


class Prescription(BaseModel):
    id: int
    patient_id: int
    encounter_id: Optional[int]
    provider_id: Optional[int]
    medication_name: str
    dosage: str
    route: str
    frequency: str
    duration: str
    quantity: str
    refills: int
    instructions: Optional[str]
    status: str
    provider_signature_path: Optional[str]
    rx_pdf_path: Optional[str]
    created_at: str
    signed_at: Optional[str]

    model_config = {"from_attributes": True}