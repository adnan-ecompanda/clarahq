from fastapi import APIRouter, Depends, HTTPException
from ..schemas_note import NoteCreate, NoteOut
from ..crud_note import (
    create_note, get_note, get_notes_for_encounter,
    update_note, delete_note
)
from ..auth import get_current_user, require_roles

router = APIRouter(prefix="/notes", tags=["Clinical Notes"])


@router.post("", response_model=NoteOut)
def add_note(
    data: NoteCreate,
    user=Depends(require_roles("admin", "doctor"))
):
    return create_note(data.model_dump())


@router.get("/{note_id}", response_model=NoteOut)
def fetch_note(
    note_id: int,
    user=Depends(get_current_user)
):
    note = get_note(note_id)
    if not note:
        raise HTTPException(404, "Note not found")
    return note


@router.get("/encounter/{encounter_id}")
def fetch_notes_for_encounter(
    encounter_id: int,
    user=Depends(get_current_user)
):
    return get_notes_for_encounter(encounter_id)


@router.put("/{note_id}", response_model=NoteOut)
def edit_note(
    note_id: int,
    data: NoteCreate,
    user=Depends(require_roles("admin", "doctor"))
):
    return update_note(note_id, data.model_dump())


@router.delete("/{note_id}")
def soft_delete_note(
    note_id: int,
    user=Depends(require_roles("admin"))
):
    return delete_note(note_id)