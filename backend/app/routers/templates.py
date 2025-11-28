from fastapi import APIRouter, HTTPException
from ..schemas_templates import (
    TemplateCreate,
    TemplateUpdate,
    TemplateView,
    TemplateVersion,
    ApplyTemplatePayload,
)
from ..crud_templates import (
    create_template,
    get_all_templates,
    get_template_by_id,
    update_template,
    delete_template,
    get_template_versions,
    rollback_template,
    apply_template,
)

router = APIRouter(prefix="/templates", tags=["Templates"])


# CREATE
@router.post("/", response_model=dict)
def create_note_template(payload: TemplateCreate):
    new_id = create_template(payload)
    return {"message": "Template created", "template_id": new_id}


# LIST ALL
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


# GET ONE
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


# UPDATE
@router.put("/{template_id}", response_model=dict)
def update_note_template(template_id: int, payload: TemplateUpdate):
    new_version = update_template(template_id, payload)
    if not new_version:
        raise HTTPException(404, "Template not found")

    return {"message": "Updated", "new_version": new_version}


# DELETE
@router.delete("/{template_id}", response_model=dict)
def remove_template(template_id: int):
    if not delete_template(template_id):
        raise HTTPException(404, "Template not found")
    return {"message": "Deleted"}


# VERSION LIST
@router.get("/{template_id}/versions", response_model=dict)
def list_versions(template_id: int):
    versions = get_template_versions(template_id)
    return {"versions": versions}


# ROLLBACK
@router.post("/{template_id}/rollback/{version}", response_model=dict)
def rollback(template_id: int, version: int):
    ok = rollback_template(template_id, version)
    if not ok:
        raise HTTPException(404, "Version not found")

    return {"message": "Rolled back", "version": version}
# =====================================================================
# APPLY TEMPLATE TO ENCOUNTER
# =====================================================================
@router.post("/apply", summary="Apply a template to an encounter")
def apply_template_to_encounter(payload: ApplyTemplatePayload):
    rendered = apply_template(payload.encounter_id, payload.template_id)

    if not rendered:
        raise HTTPException(status_code=404, detail="Encounter or Template not found")

    return {
        "success": True,
        "encounter_id": payload.encounter_id,
        "template_id": payload.template_id,
        "rendered_html": rendered
    }