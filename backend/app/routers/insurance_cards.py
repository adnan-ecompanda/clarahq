from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from ..crud_insurance_cards import (
    create_insurance_card,
    list_insurance_cards,
    get_insurance_card
)

router = APIRouter(prefix="/insurance-cards", tags=["Insurance Cards"])


@router.post("/", summary="Upload a new insurance card")
def add_insurance_card(
    patient_id: int = Form(...),
    payer_name: str = Form(...),
    plan_name: str = Form(None),
    member_id: str = Form(...),
    group_id: str = Form(None),
    relationship: str = Form(None),
    effective_date: str = Form(None),
    expiry_date: str = Form(None),
    priority: str = Form(None),
    payer_phone: str = Form(None),
    payer_address: str = Form(None),

    # FILES
    card_front: UploadFile = File(None),
    card_back: UploadFile = File(None)
):
    """
    File-upload-only endpoint.
    Receives files as multipart/form-data.
    """

    # Build a simple obj to pass to CRUD exactly as expected
    data = type("obj", (object,), {
        "patient_id": patient_id,
        "payer_name": payer_name,
        "plan_name": plan_name,
        "member_id": member_id,
        "group_id": group_id,
        "relationship": relationship,
        "effective_date": effective_date,
        "expiry_date": expiry_date,
        "priority": priority,
        "payer_phone": payer_phone,
        "payer_address": payer_address
    })

    return create_insurance_card(data, card_front, card_back)


@router.get("/patient/{patient_id}", summary="List all insurance cards for patient")
def get_cards(patient_id: int):
    return list_insurance_cards(patient_id)


@router.get("/{card_id}", summary="Get insurance card details")
def get_card(card_id: int):
    card = get_insurance_card(card_id)
    if not card:
        raise HTTPException(404, "Insurance card not found")
    return card