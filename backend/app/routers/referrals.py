import os
from fastapi import APIRouter, UploadFile, File, HTTPException

from ..crud_referrals import (
    create_referral,
    list_referrals_for_patient,
    get_referral,
    update_referral_status,
    get_referral_logs,
    add_referral_attachment,
)
from ..schemas_referrals import ReferralCreate, ReferralStatusUpdate

router = APIRouter(prefix="/referrals", tags=["Referrals"])


@router.post("/", summary="Create a new referral")
def create_ref(payload: ReferralCreate):
    return create_referral(payload)


@router.get("/patient/{patient_id}", summary="List patient referrals")
def list_for_patient(patient_id: int):
    return list_referrals_for_patient(patient_id)


@router.get("/{referral_id}", summary="Get referral details")
def read(referral_id: int):
    r = get_referral(referral_id)
    if not r:
        raise HTTPException(404, "Referral not found")
    return r


@router.put("/{referral_id}/status", summary="Update referral status")
def set_status(referral_id: int, update: ReferralStatusUpdate):
    return update_referral_status(
        referral_id,
        status=update.status,
        note=update.note
    )


@router.get("/{referral_id}/timeline", summary="Referral timeline / activity log")
def timeline(referral_id: int):
    return get_referral_logs(referral_id)


@router.post("/{referral_id}/attachments", summary="Upload referral attachment")
def upload(referral_id: int, file: UploadFile = File(...)):
    return add_referral_attachment(referral_id, file)