from pydantic import BaseModel
from typing import Optional

class ImmunizationBase(BaseModel):
    patient_id: int
    vaccine_name: str
    cvx_code: Optional[str] = None
    manufacturer: Optional[str] = None
    lot_number: Optional[str] = None
    expiration_date: Optional[str] = None
    route: Optional[str] = None
    site: Optional[str] = None
    dose: Optional[str] = None
    administered_date: Optional[str] = None
    provider_id: Optional[int] = None
    status: Optional[str] = "completed"  # completed / refused / contraindicated
    notes: Optional[str] = None
    active: Optional[int] = 1


class ImmunizationCreate(ImmunizationBase):
    pass


class ImmunizationUpdate(BaseModel):
    vaccine_name: Optional[str] = None
    cvx_code: Optional[str] = None
    manufacturer: Optional[str] = None
    lot_number: Optional[str] = None
    expiration_date: Optional[str] = None
    route: Optional[str] = None
    site: Optional[str] = None
    dose: Optional[str] = None
    administered_date: Optional[str] = None
    provider_id: Optional[int] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    active: Optional[int] = None


class ImmunizationOut(ImmunizationBase):
    id: int