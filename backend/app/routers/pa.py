from fastapi import APIRouter, HTTPException
from ..schemas_pa import PriorAuthCreate, PriorAuthRecord
from ..crud_pa import (
    create_prior_auth, get_prior_auth,
    update_prior_auth_response
)

router = APIRouter(prefix="/pa", tags=["Prior Authorization"])


@router.post("/create")
def create_pa(payload: PriorAuthCreate):
    pa_id = create_prior_auth(payload)
    return {"pa_id": pa_id, "status": "PENDING"}


@router.get("/{pa_id}")
def read_pa(pa_id: int):
    pa = get_prior_auth(pa_id)
    if not pa:
        raise HTTPException(status_code=404, detail="PA not found")
    return pa


@router.put("/{pa_id}/response")
def update_pa(pa_id: int, response_x12: str, status: str):
    if not get_prior_auth(pa_id):
        raise HTTPException(status_code=404, detail="PA not found")

    update_prior_auth_response(pa_id, response_x12, status)
    return {"pa_id": pa_id, "status": status}


@router.post("/simulate")
def simulate_pa(payload: PriorAuthCreate):
    return {
        "pa_decision": "APPROVED",
        "auth_number": "AUTH123456",
        "valid_from": "2024-01-01",
        "valid_to": "2024-12-31",
        "message": f"Procedure {payload.procedure_code} approved for patient {payload.patient_id}"
    }