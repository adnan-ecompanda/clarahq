from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os

from ..crud_patient import get_patient
from ..crud_encounter import get_encounter
from ..crud_vitals import get_latest_vitals_for_patient
from ..crud_medication import list_medications
from ..crud_allergies import list_allergies
from ..crud_problems import list_problems

from ..utils.pdf_avs import generate_avs_pdf

router = APIRouter(prefix="/patients", tags=["AVS"])


@router.get("/{patient_id}/encounters/{encounter_id}/avs")
def get_avs(patient_id: int, encounter_id: int):

    patient = get_patient(patient_id)
    if not patient:
        raise HTTPException(404, "Patient not found")

    encounter = get_encounter(encounter_id)
    if not encounter:
        raise HTTPException(404, "Encounter not found")

    vitals = get_latest_vitals_for_patient(patient_id)
    meds = list_medications(patient_id)
    allergies = list_allergies(patient_id)
    problems = list_problems(patient_id)

    output_file = f"avs_{patient_id}_{encounter_id}.pdf"
    output_path = f"temp/{output_file}"

    os.makedirs("temp", exist_ok=True)

    generate_avs_pdf(
        output_path,
        patient,
        encounter,
        vitals,
        meds,
        allergies,
        problems
    )

    return FileResponse(output_path, media_type="application/pdf", filename=output_file)