from pydantic import BaseModel
from typing import Optional

# ------------------- BASE -------------------

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None

    patient_id: Optional[int] = None
    encounter_id: Optional[int] = None

    assigned_to: Optional[int] = None  # user_id
    created_by: Optional[int] = None   # user_id

    due_date: Optional[str] = None     # ISO date

    priority: Optional[str] = "medium"   # low | medium | high | urgent
    status: Optional[str] = "pending"    # pending | in-progress | completed | cancelled

    active: Optional[int] = 1


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

    patient_id: Optional[int] = None
    encounter_id: Optional[int] = None

    assigned_to: Optional[int] = None
    due_date: Optional[str] = None

    priority: Optional[str] = None
    status: Optional[str] = None

    active: Optional[int] = None


class TaskOut(TaskBase):
    id: int