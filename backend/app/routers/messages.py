from fastapi import APIRouter, UploadFile, File, Depends
from fastapi.responses import FileResponse
from ..auth import get_current_user
from ..crud_messages import (
    create_conversation, list_conversations_for_user,
    create_message, list_messages,
    attach_file, get_attachment
)

router = APIRouter(prefix="/messages", tags=["Messages"])


@router.post("/conversation")
def start_conversation(
    participant_a: int,
    participant_b: int,
    subject: str,
    current=Depends(get_current_user)
):
    return create_conversation(current["id"], participant_a, participant_b, subject)


@router.get("/conversation")
def my_conversations(current=Depends(get_current_user)):
    return list_conversations_for_user(current["id"])


@router.post("/{conversation_id}/send")
def send_message(
    conversation_id: int,
    text: str,
    current=Depends(get_current_user)
):
    return create_message(conversation_id, current["id"], text)


@router.get("/{conversation_id}/messages")
def get_messages(conversation_id: int, current=Depends(get_current_user)):
    return list_messages(conversation_id)


@router.post("/{conversation_id}/{message_id}/attach")
def upload_message_attachment(
    conversation_id: int,
    message_id: int,
    file: UploadFile = File(...),
    current=Depends(get_current_user)
):
    return attach_file(message_id, file, conversation_id)


@router.get("/attachment/{attachment_id}/download")
def download_attachment(attachment_id: int):
    obj = get_attachment(attachment_id)
    return FileResponse(
        obj["file_path"],
        filename=obj["file_name"]
    )