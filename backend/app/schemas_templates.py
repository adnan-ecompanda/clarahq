from pydantic import BaseModel, Field
from typing import Optional


# ============================
# BASE
# ============================
class TemplateBase(BaseModel):
    name: str = Field(..., example="SOAP Progress Note")
    category: Optional[str] = Field(None, example="Primary Care")
    content_html: str = Field(..., example="<h2>Subjective</h2><p>{{patient.first_name}}...</p>")


# ============================
# CREATE
# ============================
class TemplateCreate(TemplateBase):
    created_by: Optional[int] = Field(None, example=1)


# ============================
# UPDATE
# ============================
class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    content_html: Optional[str] = None
    updated_by: Optional[int] = None


# ============================
# RESPONSE
# ============================
class TemplateResponse(TemplateBase):
    id: int

    class Config:
        from_attributes = True


# ============================
# VERSION
# ============================
class TemplateVersion(BaseModel):
    id: int
    template_id: int
    version_number: int
    content_html: str
    created_at: str

    class Config:
        from_attributes = True


# ============================
# VIEW MODEL FOR LISTING
# ============================
class TemplateView(TemplateBase):
    id: int


# ============================
# APPLY TEMPLATE Request
# ============================
class ApplyTemplatePayload(BaseModel):
    encounter_id: int = Field(..., example=101)
    template_id: int = Field(..., example=5)