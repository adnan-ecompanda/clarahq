from pydantic import BaseModel
from typing import Optional


class AppointmentCreate(BaseModel):
    patient_id: int
    provider_id: int
    start_time: str
    end_time: str
    type: Optional[str] = None
    location: Optional[str] = None
    reason: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = "scheduled"
    telehealth_url: Optional[str] = None


class AppointmentUpdate(BaseModel):
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    type: Optional[str] = None
    location: Optional[str] = None
    reason: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None
    telehealth_url: Optional[str] = None


class AppointmentOut(BaseModel):
    id: int
    patient_id: int
    provider_id: int
    start_time: str
    end_time: str
    type: Optional[str]
    location: Optional[str]
    reason: Optional[str]
    notes: Optional[str]
    status: str
    telehealth_url: Optional[str]
    active: int