from fastapi import APIRouter, HTTPException
from ..crud_telehealth import create_or_update_telehealth_link, get_telehealth_link

router = APIRouter(prefix="/telehealth", tags=["Telehealth"])


@router.post("/generate/{appointment_id}")
def generate_telehealth_link(appointment_id: int):
    return create_or_update_telehealth_link(appointment_id)


@router.get("/join/patient/{appointment_id}")
def patient_join_meeting(appointment_id: int):
    link = get_telehealth_link(appointment_id)
    if not link or not link.get("telehealth_url"):
        raise HTTPException(status_code=404, detail="Telehealth link not available")
    return {"join_url": link["telehealth_url"], "role": "patient"}


@router.get("/join/provider/{appointment_id}")
def provider_join_meeting(appointment_id: int):
    link = get_telehealth_link(appointment_id)
    if not link or not link.get("telehealth_url"):
        raise HTTPException(status_code=404, detail="Telehealth link not available")
    return {"join_url": link["telehealth_url"] + "?host=true", "role": "provider"}