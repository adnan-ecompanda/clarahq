from pydantic import BaseModel
from typing import Optional


class PatientBase(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None

    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relationship: Optional[str] = None

    insurance_provider: Optional[str] = None
    insurance_member_id: Optional[str] = None
    insurance_group_number: Optional[str] = None

    allergies: Optional[str] = None
    medications: Optional[str] = None
    chronic_conditions: Optional[str] = None

    active: Optional[int] = 1


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relationship: Optional[str] = None
    insurance_provider: Optional[str] = None
    insurance_member_id: Optional[str] = None
    insurance_group_number: Optional[str] = None
    allergies: Optional[str] = None
    medications: Optional[str] = None
    chronic_conditions: Optional[str] = None
    active: Optional[int] = None


class PatientOut(PatientBase):
    id: int