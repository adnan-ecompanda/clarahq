from pydantic import BaseModel
from typing import Optional


class SuperbillCPTBase(BaseModel):
    cpt_code: str
    units: Optional[int] = 1
    modifier: Optional[str] = None
    amount: Optional[float] = None
    icd_pointer: Optional[int] = 1


class SuperbillCPTCreate(SuperbillCPTBase):
    pass


class SuperbillCPTOut(SuperbillCPTBase):
    id: int
    superbill_id: int


class SuperbillICDBase(BaseModel):
    icd_code: str
    description: Optional[str] = None


class SuperbillICDCreate(SuperbillICDBase):
    pass


class SuperbillICDOut(SuperbillICDBase):
    id: int
    superbill_id: int