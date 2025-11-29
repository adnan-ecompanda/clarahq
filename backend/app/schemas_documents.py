from pydantic import BaseModel
from typing import Optional

class DocumentUploadBase64(BaseModel):
    patient_id: int
    file_name: str
    file_type: str   # pdf/png/jpg/docx
    base64_data: str


class DocumentItem(BaseModel):
    id: int
    patient_id: int
    file_name: str
    file_type: str
    file_size: int
    file_path: str
    uploaded_at: str
class DocumentBase(BaseModel):
    patient_id: int
    category: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None

class DocumentOut(DocumentBase):
    id: int
    file_name: str
    file_path: str
    file_type: str
    file_size: int
    uploaded_by: int
    uploaded_at: str
    active: int

    class Config:
        orm_mode = True