from fastapi import APIRouter, HTTPException
from ..crud_claims import create_claim_from_superbill, get_claim
from ..schemas_claims import ClaimResponse

router = APIRouter(prefix="/claims", tags=["Claims"])


@router.post("/from-superbill/{sb_id}", response_model=ClaimResponse)
def create_claim(sb_id: int):
    try:
        return create_claim_from_superbill(sb_id)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/{claim_id}", response_model=ClaimResponse)
def get_claim_endpoint(claim_id: int):
    claim = get_claim(claim_id)
    if not claim:
        raise HTTPException(404, "Claim not found")
    return claim