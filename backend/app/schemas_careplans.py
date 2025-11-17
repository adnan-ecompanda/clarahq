from pydantic import BaseModel
from typing import Optional

class CarePlanBase(BaseModel):
    patient_id: int
    encounter_id: Optional[int] = None
    provider_id: Optional[int] = None

    title: str
    diagnosis: Optional[str] = None

    goals: Optional[str] = None
    interventions: Optional[str] = None
    expected_outcomes: Optional[str] = None
    actual_outcomes: Optional[str] = None

    start_date: Optional[str] = None
    review_date: Optional[str] = None
    status: Optional[str] = "active"  # active / completed

    active: Optional[int] = 1


class CarePlanCreate(CarePlanBase):
    pass


class CarePlanUpdate(BaseModel):
    title: Optional[str] = None
    diagnosis: Optional[str] = None
    goals: Optional[str] = None
    interventions: Optional[str] = None
    expected_outcomes: Optional[str] = None
    actual_outcomes: Optional[str] = None
    start_date: Optional[str] = None
    review_date: Optional[str] = None
    status: Optional[str] = None
    provider_id: Optional[int] = None
    encounter_id: Optional[int] = None
    active: Optional[int] = None


class CarePlanOut(CarePlanBase):
    id: int