from fastapi import APIRouter, HTTPException
from ..schemas_eligibility import EligibilityRequest, EligibilityRecord
from ..crud_eligibility import (
    create_eligibility_request,
    get_eligibility_request,
    attach_eligibility_response
)

router = APIRouter(prefix="/eligibility", tags=["Eligibility"])


# ------------------------------
# CREATE Eligibility (DB Write)
# ------------------------------
@router.post("/create")
def create_elig(req: EligibilityRequest):
    new_id = create_eligibility_request(req)
    return {"id": new_id, "status": "PENDING"}


# ------------------------------
# GET Eligibility Record
# ------------------------------
@router.get("/{req_id}", response_model=EligibilityRecord)
def read_elig(req_id: int):
    record = get_eligibility_request(req_id)
    if not record:
        raise HTTPException(status_code=404, detail="Eligibility request not found")
    return record


# ------------------------------
# UPDATE Eligibility Response
# ------------------------------
@router.put("/{req_id}/response")
def update_elig(req_id: int, response_x12: str, status: str):
    ok = attach_eligibility_response(req_id, response_x12, status)
    if not ok:
        raise HTTPException(status_code=404, detail="Eligibility request not found")
    return {"success": True, "message": "Eligibility response updated"}


# ------------------------------
# OPTIONAL — Simulation Endpoint
# ------------------------------
@router.post("/simulate")
def simulate_elig(req: EligibilityRequest):
    return {
        "status": "inactive",
        "co_pay": 10,
        "deductible_remaining": 750,
        "out_of_pocket_max": 5000,
        "effective_date": "2024-01-01",
        "expiration_date": "2024-12-31",
        "plan_type": "PPO"
    }
