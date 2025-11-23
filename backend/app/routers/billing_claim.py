from fastapi import APIRouter, HTTPException
from app.utils.claim_generator import (
    load_superbill,
    generate_claim_json,
    generate_x12_837p
)

router = APIRouter(
    prefix="/billing/claim",
    tags=["Billing – Claim Generator"]
)


@router.get("/{sb_id}/json")
def claim_json(sb_id: int):
    bundle = load_superbill(sb_id)
    if not bundle:
        raise HTTPException(404, "Superbill not found")
    return generate_claim_json(bundle)


@router.get("/{sb_id}/x12")
def claim_x12(sb_id: int):
    bundle = load_superbill(sb_id)
    if not bundle:
        raise HTTPException(404, "Superbill not found")

    x12 = generate_x12_837p(bundle)
    return {"x12": x12}