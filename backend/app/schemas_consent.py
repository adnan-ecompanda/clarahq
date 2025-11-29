from pydantic import BaseModel
from typing import Optional

class ConsentCreate(BaseModel):
    patient_id: int
    consent_type: str
    html_content: str

class ConsentSign(BaseModel):
    patient_id: int
    signature_base64: str
    signed_at: str  # ISO datetime

class ConsentRecord(BaseModel):
    id: int
    patient_id: int
    consent_type: str
    html_content: str
    signature_path: Optional[str]
    pdf_path: Optional[str]
    created_at: str
    signed_at: Optional[str]

    class Config:
        from_attributes = True