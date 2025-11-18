from fastapi import APIRouter, UploadFile, File

from ..crud_portal_messages import (
    create_thread, list_threads_for_patient, send_message,
    get_messages, add_message_attachment, mark_message_read
)
from ..schemas_portal_messages import ThreadCreate, MessageCreate


router = APIRouter(prefix="/portal/messages", tags=["Portal Messaging"])


@router.post("/thread")
def create_new_thread(data: ThreadCreate):
    return create_thread(data.patient_id, data.provider_id, data.subject)


@router.get("/threads/{patient_id}")
def get_patient_threads(patient_id: int):
    return list_threads_for_patient(patient_id)


@router.post("/{thread_id}/send")
def send_portal_message(thread_id: int, data: MessageCreate):
    return send_message(thread_id, data.sender_type, data.sender_id, data.content)


@router.get("/{thread_id}/messages")
def get_thread_messages(thread_id: int):
    return get_messages(thread_id)


@router.post("/message/{message_id}/attachment")
def upload_message_attachment(message_id: int, file: UploadFile = File(...)):
    return add_message_attachment(message_id, file)


@router.put("/message/{message_id}/read")
def mark_read(message_id: int):
    return mark_message_read(message_id)