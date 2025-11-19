from pydantic import BaseModel

class PortalLoginRequest(BaseModel):
    email: str
    dob: str  # YYYY-MM-DD

class PortalLoginResponse(BaseModel):
    token: str
    patient_id: int
    first_name: str
    last_name: str