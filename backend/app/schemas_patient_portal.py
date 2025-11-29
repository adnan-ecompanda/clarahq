from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# -----------------------
# Patient Portal: Auth
# -----------------------

class PatientRegister(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str


class PatientLogin(BaseModel):
    email: str
    password: str


class PatientPortalProfile(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    dob: Optional[str] = None

    class Config:
        from_attributes = True


class PatientPortalProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    dob: Optional[str] = None
    gender: Optional[str] = None
    phone_primary: Optional[str] = None
    email: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relationship: Optional[str] = None
    insurance_provider: Optional[str] = None
    insurance_member_id: Optional[str] = None
    insurance_group_number: Optional[str] = None
    allergies: Optional[str] = None
    medications: Optional[str] = None
    chronic_conditions: Optional[str] = None


# -----------------------
# Encounters
# -----------------------

class EncounterSummary(BaseModel):
    id: int
    visit_date: str
    visit_type: Optional[str]
    chief_complaint: Optional[str]


class EncounterDetail(BaseModel):
    id: int
    visit_date: str
    visit_type: Optional[str]
    chief_complaint: Optional[str]
    hpi: Optional[str]
    objective_exam: Optional[str]
    assessment: Optional[str]
    plan: Optional[str]
    vitals_bp: Optional[str]
    vitals_hr: Optional[str]
    vitals_temp: Optional[str]
    vitals_rr: Optional[str]
    vitals_spo2: Optional[str]
    cpt_code: Optional[str]
    icd10_code: Optional[str]


# -----------------------
# Claims
# -----------------------

class ClaimSummary(BaseModel):
    id: int
    superbill_id: Optional[int]
    status: Optional[str]
    created_at: Optional[str]


class ClaimDetail(BaseModel):
    id: int
    superbill_id: Optional[int]
    provider_id: Optional[int]
    patient_id: int
    status: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]


# -----------------------
# Documents
# -----------------------

class PortalDocument(BaseModel):
    id: int
    file_name: str
    file_type: str
    file_size: int
    file_path: str
    uploaded_at: str