from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from typing import Optional

from ..auth import get_current_user, require_roles
from ..crud_results import (
    create_lab_result, get_lab_result, update_lab_result, list_lab_results,
    create_imaging_result, get_imaging_result, update_imaging_result, list_imaging_results, save_imaging_attachment
)
from ..schemas_results import (
    LabResultCreate, LabResultUpdate, LabResultOut,
    ImagingResultCreate, ImagingResultUpdate, ImagingResultOut
)

router = APIRouter(prefix="/results", tags=["Lab & Imaging Results"])

# ------- LAB RESULTS --------

@router.post("/lab", response_model=LabResultOut)
def create_lab(data: LabResultCreate, user=Depends(require_roles("admin", "provider"))):
    return create_lab_result(data)

@router.get("/lab/{result_id}", response_model=LabResultOut)
def get_lab(result_id: int, user=Depends(get_current_user)):
    result = get_lab_result(result_id)
    if not result:
        raise HTTPException(404, "Lab result not found")
    return result

@router.put("/lab/{result_id}", response_model=LabResultOut)
def update_lab(result_id: int, data: LabResultUpdate, user=Depends(require_roles("admin", "provider"))):
    return update_lab_result(result_id, data)


# ------- IMAGING RESULTS --------

@router.post("/imaging", response_model=ImagingResultOut)
def create_imaging(data: ImagingResultCreate, user=Depends(require_roles("admin", "provider"))):
    return create_imaging_result(data)

@router.get("/imaging/{result_id}", response_model=ImagingResultOut)
def get_imaging(result_id: int, user=Depends(get_current_user)):
    result = get_imaging_result(result_id)
    if not result:
        raise HTTPException(404, "Imaging result not found")
    return result

@router.put("/imaging/{result_id}", response_model=ImagingResultOut)
def update_imaging(result_id: int, data: ImagingResultUpdate, user=Depends(require_roles("admin", "provider"))):
    return update_imaging_result(result_id, data)

@router.post("/imaging/{result_id}/upload")
async def upload_imaging_attachment(
    result_id: int,
    file: UploadFile = File(...),
    current_user = Depends(require_roles("admin", "provider"))
):
    return save_imaging_attachment(result_id, file)