from pydantic import BaseModel
from typing import Optional

# ------- LAB RESULTS --------
class LabResultCreate(BaseModel):
    order_id: int
    patient_id: int
    provider_id: int
    encounter_id: Optional[int] = None

    test_name: str
    value: Optional[str] = None
    unit: Optional[str] = None
    reference_range: Optional[str] = None
    abnormal_flag: Optional[str] = None
    notes: Optional[str] = None
    result_date: Optional[str] = None


class LabResultUpdate(BaseModel):
    value: Optional[str] = None
    unit: Optional[str] = None
    reference_range: Optional[str] = None
    abnormal_flag: Optional[str] = None
    notes: Optional[str] = None
    result_date: Optional[str] = None
    active: Optional[int] = None


class LabResultOut(BaseModel):
    id: int
    order_id: int
    patient_id: int
    provider_id: int
    encounter_id: Optional[int]

    test_name: str
    value: Optional[str]
    unit: Optional[str]
    reference_range: Optional[str]
    abnormal_flag: Optional[str]
    notes: Optional[str]
    result_date: str
    active: int

    created_at: str
    updated_at: str


# ------- IMAGING RESULTS --------
class ImagingResultCreate(BaseModel):
    order_id: int
    patient_id: int
    provider_id: int
    encounter_id: Optional[int] = None

    modality: str
    body_part: Optional[str] = None
    impression: Optional[str] = None
    findings: Optional[str] = None
    radiologist: Optional[str] = None
    result_date: Optional[str] = None


class ImagingResultUpdate(BaseModel):
    body_part: Optional[str] = None
    impression: Optional[str] = None
    findings: Optional[str] = None
    radiologist: Optional[str] = None
    result_date: Optional[str] = None
    active: Optional[int] = None


class ImagingResultOut(BaseModel):
    id: int
    order_id: int
    patient_id: int
    provider_id: int
    encounter_id: Optional[int]

    modality: str
    body_part: Optional[str]
    impression: Optional[str]
    findings: Optional[str]
    radiologist: Optional[str]
    result_date: str
    active: int

    created_at: str
    updated_at: str

class ImagingAttachment(BaseModel):
    id: int
    file_name: str
    file_path: str
    file_type: str
    uploaded_at: str

class ImagingResultOut(BaseModel):
    id: int
    order_id: int | None
    patient_id: int
    provider_id: int | None
    encounter_id: int | None

    study_type: str
    body_part: str | None
    findings: str | None
    impression: str | None
    result_date: str
    active: int

    attachments: list[ImagingAttachment] = []