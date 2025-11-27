from pydantic import BaseModel, Field
from typing import Optional


class TemplateBase(BaseModel):
    name: str = Field(..., example="SOAP Progress Note")
    category: Optional[str] = Field(None, example="Primary Care")
    content_html: str = Field(..., example="<h2>Subjective</h2><p>{{patient.first_name}} reports...</p>")


class TemplateCreate(TemplateBase):
    pass


class TemplateUpdate(TemplateBase):
    pass


class TemplateView(TemplateBase):
    id: int

    class Config:
        from_attributes = True  # replaces orm_mode