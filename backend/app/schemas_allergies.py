from pydantic import BaseModel
from typing import Optional

class AllergyBase(BaseModel):
    patient_id: int
    allergen: str
    reaction: Optional[str] = None
    severity: Optional[str] = None   # mild | moderate | severe
    notes: Optional[str] = None
    recorded_by: Optional[int] = None


class AllergyCreate(AllergyBase):
    pass


class AllergyUpdate(BaseModel):
    allergen: Optional[str] = None
    reaction: Optional[str] = None
    severity: Optional[str] = None
    notes: Optional[str] = None
    active: Optional[int] = None


class AllergyOut(AllergyBase):
    id: int
    active: int
    recorded_at: Optional[str]

    class Config:
        from_attributes = True