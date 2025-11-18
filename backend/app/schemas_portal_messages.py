from pydantic import BaseModel


class ThreadCreate(BaseModel):
    patient_id: int
    provider_id: int
    subject: str


class MessageCreate(BaseModel):
    sender_type: str  # 'patient' or 'provider'
    sender_id: int
    content: str


class ThreadOut(BaseModel):
    id: int
    patient_id: int
    provider_id: int
    subject: str
    status: str
    created_at: str
    updated_at: str


class MessageOut(BaseModel):
    id: int
    thread_id: int
    sender_type: str
    sender_id: int
    content: str
    is_read: int
    created_at: str