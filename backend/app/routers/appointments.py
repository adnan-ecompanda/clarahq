from fastapi import APIRouter, Depends, HTTPException
from ..auth import require_roles, get_current_user
from ..schemas_appointments import AppointmentCreate, AppointmentUpdate
from ..crud_appointments import (
    create_appointment, get_appointment, list_appointments,
    update_appointment, delete_appointment, log_appointment_action
)

router = APIRouter(prefix="/appointments", tags=["Appointments"])


@router.post("", summary="Create appointment")
def create_appt(data: AppointmentCreate, current_user=Depends(require_roles("admin", "provider"))):
    appt = create_appointment(data.model_dump())
    log_appointment_action(appt["id"], "created", current_user["id"])
    return appt


@router.get("/{appt_id}", summary="Get appointment")
def get_appt(appt_id: int, current_user=Depends(get_current_user)):
    appt = get_appointment(appt_id)
    if not appt:
        raise HTTPException(404, "Appointment not found")
    return appt


@router.get("", summary="List appointments")
def list_appts(provider_id: int = None, patient_id: int = None, current_user=Depends(get_current_user)):
    return list_appointments(provider_id, patient_id)


@router.put("/{appt_id}", summary="Update appointment")
def update_appt(appt_id: int, data: AppointmentUpdate, current_user=Depends(require_roles("admin", "provider"))):
    updated = update_appointment(appt_id, {k: v for k, v in data.model_dump().items() if v is not None})
    log_appointment_action(appt_id, "updated", current_user["id"])
    return updated


@router.delete("/{appt_id}", summary="Cancel appointment")
def cancel_appt(appt_id: int, current_user=Depends(require_roles("admin", "provider"))):
    delete_appointment(appt_id)
    log_appointment_action(appt_id, "cancelled", current_user["id"])
    return {"message": "Appointment cancelled"}