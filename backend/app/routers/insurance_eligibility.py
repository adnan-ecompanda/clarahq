from fastapi import APIRouter, HTTPException

from ..schemas_insurance_eligibility import EligibilityRequest, EligibilityResponse
from ..utils.eligibility_engine import mock_eligibility_check

router = APIRouter(prefix="/eligibility", tags=["Insurance Eligibility"])


@router.post("/", response_model=EligibilityResponse)
def check_eligibility(payload: EligibilityRequest):
    result = mock_eligibility_check(
        provider=payload.insurance_provider,
        member_id=payload.member_id
    )
    return result