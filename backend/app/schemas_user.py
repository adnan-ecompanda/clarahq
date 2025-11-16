from pydantic import BaseModel, EmailStr
from typing import Optional


class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None

    role: str  # admin/provider/nurse/etc.
    department: Optional[str] = None
    specialty: Optional[str] = None

    npi_number: Optional[str] = None
    credentials: Optional[str] = None  # MD, RN, CST, etc.
    license_number: Optional[str] = None
    license_state: Optional[str] = None

    profile_photo_url: Optional[str] = None
    language_preference: Optional[str] = "English"
    notification_preferences: Optional[str] = None  # JSON string
    active: bool = True


class UserCreate(UserBase):
    password: str  # plaintext input (we will hash it)


class UserOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    role: str
    department: Optional[str] = None
    specialty: Optional[str] = None
    npi_number: Optional[str] = None
    credentials: Optional[str] = None
    license_number: Optional[str] = None
    license_state: Optional[str] = None
    profile_photo_url: Optional[str] = None
    language_preference: Optional[str] = None
    notification_preferences: Optional[str] = None

    active: int   # 🔥 ADD THIS LINE

    class Config:
        from_attributes = True


class LoginInput(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"