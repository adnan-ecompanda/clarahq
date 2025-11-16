from pydantic import BaseModel, EmailStr
from typing import Optional


class PatientBase(BaseModel):
    # Identification
    mrn: Optional[str] = None
    external_id: Optional[str] = None

    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    dob: Optional[str] = None  # ISO date (YYYY-MM-DD)

    gender: Optional[str] = None  # male/female/other/unknown
    photo_url: Optional[str] = None

    # Contact
    phone_primary: Optional[str] = None
    phone_secondary: Optional[str] = None
    email: Optional[EmailStr] = None

    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = "USA"

    # Emergency contact
    emergency_contact_name: Optional[str] = None
    emergency_contact_relationship: Optional[str] = None
    emergency_contact_phone: Optional[str] = None

    # Insurance
    insurance_provider: Optional[str] = None
    insurance_plan: Optional[str] = None
    insurance_member_id: Optional[str] = None
    insurance_group_number: Optional[str] = None
    insurance_effective_date: Optional[str] = None
    insurance_expiration_date: Optional[str] = None

    # Clinical flags
    allergies: Optional[str] = None
    medications: Optional[str] = None
    notes: Optional[str] = None

    preferred_language: Optional[str] = "English"
    requires_interpreter: bool = False
    is_active: bool = True


class PatientCreate(PatientBase):
    """
    For now, create = all fields optional except first_name, last_name.
    """
    pass


class PatientOut(PatientBase):
    id: int

    class Config:
        from_attributes = True