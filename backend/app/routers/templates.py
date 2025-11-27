from fastapi import APIRouter, HTTPException
from ..schemas_templates import (
    TemplateCreate, TemplateUpdate, TemplateView
)
from ..crud_templates import (
    create_template,
    get_all_templates,
    get_template_by_id,
    update_template,
    delete_template,
    apply_template_to_encounter
)

router = APIRouter(prefix="/templates", tags=["Templates"])


# -----------------------------------------------------
# CREATE TEMPLATE
# -----------------------------------------------------
@router.post("/", response_model=dict)
def create_note_template(payload: TemplateCreate):
    new_id = create_template(payload)
    return {"message": "Template created", "template_id": new_id}


# -----------------------------------------------------
# GET ALL
# -----------------------------------------------------
@router.get("/", response_model=list[TemplateView])
def list_templates():
    rows = get_all_templates()
    return [
        TemplateView(
            id=r[0],
            name=r[1],
            category=r[2],
            content_html=r[3]
        )
        for r in rows
    ]


# -----------------------------------------------------
# GET ONE
# -----------------------------------------------------
@router.get("/{template_id}", response_model=TemplateView)
def get_template(template_id: int):
    tpl = get_template_by_id(template_id)
    if not tpl:
        raise HTTPException(404, "Template not found")

    return TemplateView(
        id=tpl[0],
        name=tpl[1],
        category=tpl[2],
        content_html=tpl[3]
    )


# -----------------------------------------------------
# UPDATE
# -----------------------------------------------------
@router.put("/{template_id}", response_model=dict)
def update_note_template(template_id: int, payload: TemplateUpdate):
    if not update_template(template_id, payload):
        raise HTTPException(404, "Template not found")

    return {"message": "Updated successfully"}


# -----------------------------------------------------
# DELETE
# -----------------------------------------------------
@router.delete("/{template_id}", response_model=dict)
def remove_template(template_id: int):
    if not delete_template(template_id):
        raise HTTPException(404, "Template not found")

    return {"message": "Deleted"}


# -----------------------------------------------------
# APPLY TEMPLATE TO ENCOUNTER
# -----------------------------------------------------
@router.post("/{template_id}/apply", response_model=dict)
def apply_to_encounter(template_id: int, encounter_data: dict):
    result = apply_template_to_encounter(template_id, encounter_data)
    if not result:
        raise HTTPException(404, "Template not found")

    return result