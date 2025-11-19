from fastapi import APIRouter, HTTPException
from ..schemas_portal_auth import PortalLoginRequest, PortalLoginResponse
from ..crud_portal_auth import authenticate_portal_patient, create_portal_jwt

router = APIRouter(prefix="/portal", tags=["Portal Auth"])


@router.post("/login", response_model=PortalLoginResponse)
def portal_patient_login(data: PortalLoginRequest):
    patient = authenticate_portal_patient(data.email, data.dob)

    if not patient:
        raise HTTPException(status_code=401, detail="Invalid email or DOB")

    token = create_portal_jwt(patient)

    return PortalLoginResponse(
        token=token,
        patient_id=patient["id"],
        first_name=patient["first_name"],
        last_name=patient["last_name"]
    )