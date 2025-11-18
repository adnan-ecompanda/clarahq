from pydantic import BaseModel
from typing import Optional

class InsuranceCreate(BaseModel):
    payer_name: Optional[str]
    plan_name: Optional[str]
    member_id: Optional[str]
    group_id: Optional[str]
    relationship: Optional[str]
    effective_date: Optional[str]
    expiry_date: Optional[str]
    phone: Optional[str]
    payer_address: Optional[str]
    priority: Optional[int] = 1
    card_front: Optional[str] = None
    card_back: Optional[str] = None

class InsuranceUpdate(InsuranceCreate):
    pass