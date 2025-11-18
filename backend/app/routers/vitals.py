from fastapi import APIRouter, HTTPException

from ..schemas_vitals import VitalsCreate, FlowsheetRowCreate
from ..crud_vitals import (
    add_vitals, get_vitals, list_vitals_for_patient,
    add_flowsheet_row, get_flowsheet_row, list_flowsheet
)

router = APIRouter(prefix="/vitals", tags=["Vitals & Flowsheets"])


# -----------------------------
# Basic vitals
# -----------------------------
@router.post("/", summary="Record basic vitals")
def create_vitals(payload: VitalsCreate):
    return add_vitals(payload)


@router.get("/{vital_id}", summary="Get vitals entry")
def read_vitals(vital_id: int):
    v = get_vitals(vital_id)
    if not v:
        raise HTTPException(404, "Vitals not found")
    return v


@router.get("/patient/{patient_id}", summary="List patient vitals")
def list_for_patient(patient_id: int):
    return list_vitals_for_patient(patient_id)


# -----------------------------
# Flowsheet
# -----------------------------
@router.post("/flowsheet", summary="Add flowsheet row")
def create_flowsheet_row(payload: FlowsheetRowCreate):
    return add_flowsheet_row(payload)


@router.get("/flowsheet/{row_id}", summary="Get flowsheet row")
def read_flowsheet_row(row_id: int):
    r = get_flowsheet_row(row_id)
    if not r:
        raise HTTPException(404, "Flowsheet row not found")
    return r


@router.get("/flowsheet/patient/{patient_id}", summary="List flowsheet rows for patient")
def list_patient_flowsheet(patient_id: int, panel: str | None = None):
    return list_flowsheet(patient_id, panel)