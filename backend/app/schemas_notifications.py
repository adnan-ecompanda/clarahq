from pydantic import BaseModel

class NotificationCreate(BaseModel):
    user_id: int
    title: str
    message: str
    type: str
    ref_id: int | None = None