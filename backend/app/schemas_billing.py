from pydantic import BaseModel
from typing import Optional

# ------------------ BILLING CODES ------------------

class BillingCodeBase(BaseModel):
    code: str
    code_type: str  # "CPT", "HCPCS", "ICD10"
    description: Optional[str] = None
    amount: Optional[float] = 0.0
    active: Optional[int] = 1


class BillingCodeCreate(BillingCodeBase):
    pass


class BillingCodeUpdate(BaseModel):
    code: Optional[str] = None
    code_type: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[float] = None
    active: Optional[int] = None


class BillingCodeOut(BillingCodeBase):
    id: int


# ------------------ SUPERBILLS ------------------

class SuperbillBase(BaseModel):
    encounter_id: int
    patient_id: int
    provider_id: int

    cpt_code: Optional[str] = None
    icd10_code: Optional[str] = None

    units: Optional[int] = 1
    modifier: Optional[str] = None
    notes: Optional[str] = None

    status: Optional[str] = "draft"  # draft, submitted, billed, denied, paid

    active: Optional[int] = 1


class SuperbillCreate(SuperbillBase):
    pass


class SuperbillUpdate(BaseModel):
    cpt_code: Optional[str] = None
    icd10_code: Optional[str] = None
    units: Optional[int] = None
    modifier: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None
    active: Optional[int] = None


class SuperbillOut(SuperbillBase):
    id: int