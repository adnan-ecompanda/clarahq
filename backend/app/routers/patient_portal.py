from fastapi import APIRouter, HTTPException
from ..schemas_patient_portal import (
    PatientRegister, PatientLogin, PatientPortalProfileUpdate
)
from ..crud_patient_portal import *

router = APIRouter(prefix="/patient-portal", tags=["Patient Portal"])


# -----------------------
# Registration
# -----------------------

@router.post("/register")
def register(data: PatientRegister):
    return register_patient(data)


@router.post("/login")
def login(data: PatientLogin):
    result = login_patient(data)
    if not result:
        raise HTTPException(400, "Invalid credentials")
    return result


# -----------------------
# Profile
# -----------------------

@router.get("/{patient_id}/profile")
def get_profile(patient_id: int):
    profile = get_patient_profile(patient_id)
    if not profile:
        raise HTTPException(404, "Patient not found")
    return profile


@router.put("/{patient_id}/profile")
def update_profile(patient_id: int, data: PatientPortalProfileUpdate):
    return update_patient_profile(patient_id, data)


# -----------------------
# Encounters
# -----------------------

@router.get("/{patient_id}/encounters")
def encounters(patient_id: int):
    return list_encounters(patient_id)


@router.get("/{patient_id}/encounters/{encounter_id}")
def encounter_details(patient_id: int, encounter_id: int):
    detail = encounter_detail(encounter_id)
    if not detail:
        raise HTTPException(404, "Encounter not found")
    return detail


# -----------------------
# Claims
# -----------------------

@router.get("/{patient_id}/claims")
def claims_list(patient_id: int):
    return list_claims(patient_id)


@router.get("/{patient_id}/claims/{claim_id}")
def claim_details(patient_id: int, claim_id: int):
    detail = claim_detail(claim_id)
    if not detail:
        raise HTTPException(404, "Claim not found")
    return detail


# -----------------------
# Documents
# -----------------------

@router.get("/{patient_id}/documents/encounter/{encounter_id}")
def encounter_docs(patient_id: int, encounter_id: int):
    return documents_for_encounter(encounter_id)


@router.get("/{patient_id}/documents/claim/{claim_id}")
def claim_docs(patient_id: int, claim_id: int):
    return documents_for_claim(claim_id)