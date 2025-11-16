from fastapi import APIRouter, Depends, HTTPException
from ..auth import require_roles
from ..schemas_encounter import EncounterCreate, EncounterUpdate, EncounterOut
from ..crud_encounter import (
    create_encounter,
    list_encounters,
    get_encounter,
    update_encounter,
    delete_encounter,
    list_patient_encounters
)

router = APIRouter(prefix="/encounters", tags=["Encounters"])


@router.post("", response_model=EncounterOut)
def create(data: EncounterCreate, user=Depends(require_roles("admin", "provider"))):
    return create_encounter(data)


@router.get("", response_model=list[EncounterOut])
def list_all(user=Depends(require_roles("admin", "provider"))):
    return list_encounters()


@router.get("/{encounter_id}", response_model=EncounterOut)
def get(encounter_id: int, user=Depends(require_roles("admin", "provider"))):
    item = get_encounter(encounter_id)
    if not item:
        raise HTTPException(404, "Encounter not found")
    return item


@router.get("/patient/{patient_id}", response_model=list[EncounterOut])
def list_for_patient(patient_id: int, user=Depends(require_roles("admin", "provider"))):
    return list_patient_encounters(patient_id)


@router.put("/{encounter_id}", response_model=EncounterOut)
def update(encounter_id: int, data: EncounterUpdate, user=Depends(require_roles("admin", "provider"))):
    p = update_encounter(encounter_id, data)
    if not p:
        raise HTTPException(404, "Encounter not found")
    return p


@router.delete("/{encounter_id}")
def delete(encounter_id: int, user=Depends(require_roles("admin"))):
    delete_encounter(encounter_id)
    return {"message": "Encounter deleted"}