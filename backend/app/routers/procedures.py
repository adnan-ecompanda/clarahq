from fastapi import APIRouter, HTTPException, Depends
from ..auth import require_roles
from ..schemas_procedures import ProcedureCreate, ProcedureUpdate
from ..crud_procedures import (
    create_procedure, get_procedure,
    list_patient_procedures, update_procedure,
    delete_procedure
)

router = APIRouter(prefix="/procedures", tags=["Procedures"])


@router.post("/", dependencies=[Depends(require_roles("admin", "provider"))])
def create_proc(data: ProcedureCreate):
    return create_procedure(data)


@router.get("/{proc_id}")
def get_proc(proc_id: int):
    rec = get_procedure(proc_id)
    if not rec:
        raise HTTPException(404, "Procedure not found")
    return rec


@router.get("/patient/{patient_id}")
def list_procs(patient_id: int):
    return list_patient_procedures(patient_id)


@router.put("/{proc_id}", dependencies=[Depends(require_roles("admin", "provider"))])
def update_proc(proc_id: int, data: ProcedureUpdate):
    return update_procedure(proc_id, data)


@router.delete("/{proc_id}", dependencies=[Depends(require_roles("admin"))])
def delete_proc(proc_id: int):
    return delete_procedure(proc_id)