from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from ..schemas_prescriptions import PrescriptionCreate, PrescriptionOut
from ..crud_prescriptions import (
    create_prescription,
    get_prescription
)
from ..utils.rx_pdf import generate_rx_pdf

router = APIRouter(prefix="/prescriptions", tags=["eRx"])


@router.post("/", response_model=PrescriptionOut)
def create_rx(payload: PrescriptionCreate):
    rx = create_prescription(payload.dict())
    return rx


@router.get("/{rx_id}/pdf")
def download_rx_pdf(rx_id: int):
    rx = get_prescription(rx_id)
    if not rx:
        raise HTTPException(status_code=404, detail="Prescription not found")

    path = generate_rx_pdf(rx)
    return FileResponse(path, media_type="application/pdf", filename=f"rx_{rx_id}.pdf")