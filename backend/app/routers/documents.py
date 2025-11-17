import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from ..crud_documents import get_document, create_document, get_documents_for_patient
from ..auth import get_current_user, require_roles
from fastapi import UploadFile, File, Form, Depends

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", summary="Upload a document for a patient")
def upload_document(
    patient_id: int = Form(...),
    category: str = Form(None),
    title: str = Form(None),
    description: str = Form(None),
    file: UploadFile = File(...),
    current_user=Depends(get_current_user)
):
    doc = create_document(
        patient_id=patient_id,
        user_id=current_user["id"],
        category=category,
        title=title,
        description=description,
        file=file
    )
    return doc


@router.get("/patient/{patient_id}")
def list_documents(patient_id: int):
    return get_documents_for_patient(patient_id)


@router.get("/download/{doc_id}", summary="Download patient document")
def download_document(doc_id: int):
    doc = get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    file_path = doc.file_path

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File missing on server")

    return FileResponse(
        path=file_path,
        filename=doc.file_name,
        media_type=doc.file_type or "application/octet-stream"
    )