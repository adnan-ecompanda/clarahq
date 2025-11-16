from pydantic import BaseModel
from typing import Optional


class NoteCreate(BaseModel):
    encounter_id: int
    provider_id: int
    note_type: str
    content: str
    signed_by: Optional[int] = None
    signed_at: Optional[str] = None
    active: int = 1


class NoteOut(BaseModel):
    id: int
    encounter_id: int
    provider_id: int
    note_type: str
    content: str
    signed_by: Optional[int]
    signed_at: Optional[str]
    active: int
    created_at: str
    updated_at: str