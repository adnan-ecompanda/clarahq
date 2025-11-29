from fastapi import APIRouter, HTTPException
from ..schemas_consent import ConsentCreate, ConsentSign
from ..crud_consent import (
    create_consent,
    sign_consent,
    get_consent
)

router = APIRouter(prefix="/consent", tags=["Consent Forms"])


@router.post("/create")
def create(data: ConsentCreate):
    return create_consent(data)


@router.put("/{consent_id}/sign")
def sign(consent_id: int, data: ConsentSign):
    result = sign_consent(consent_id, data)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.get("/{consent_id}")
def read(consent_id: int):
    result = get_consent(consent_id)
    if not result:
        raise HTTPException(status_code=404, detail="Consent not found")
    return result