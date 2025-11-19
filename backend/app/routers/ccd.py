from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse, JSONResponse
import tempfile
import os

from ..crud_patient import get_patient
from ..crud_allergies import list_allergies
from ..crud_medication import list_medications
from ..crud_problems import list_problems
from ..crud_procedures import list_procedures
from ..crud_vitals import list_vitals_for_patient
from ..crud_encounter import list_encounters_for_patient
from ..crud_results import list_lab_results_for_patient, list_imaging_results_for_patient
from ..crud_careplans import list_careplans_for_patient
from ..crud_immunization import list_immunizations

from ..utils.ccd_builder import build_ccd, pretty_xml
from ..utils.fhir_converter import convert_to_fhir

router = APIRouter(prefix="/patients", tags=["CCD Summary"])


def get_all_sections(patient_id: int):
    """Helper to prevent repeating code."""
    allergies = list_allergies(patient_id)
    meds = list_medications(patient_id)
    problems = list_problems(patient_id)
    immunizations = list_immunizations(patient_id)
    procedures = list_procedures(patient_id)
    vitals = list_vitals_for_patient(patient_id)
    encounters = list_encounters_for_patient(patient_id)
    labs = list_lab_results_for_patient(patient_id)
    imaging = list_imaging_results_for_patient(patient_id)
    careplans = list_careplans_for_patient(patient_id)

    return allergies, meds, problems, immunizations, procedures, vitals, encounters, labs, imaging, careplans


# ---------------------------------------------------------------------
# 1️⃣ NORMAL CCD API (returns XML)
# ---------------------------------------------------------------------
@router.get("/{patient_id}/ccd", summary="Generate CCD (XML)")
def generate_ccd(patient_id: int):
    patient = get_patient(patient_id)
    if not patient:
        raise HTTPException(404, "Patient not found")

    patient_data = patient.model_dump()
    patient_data["name"] = f"{patient.first_name} {patient.last_name}"
    patient_data["dob"] = patient.dob or ""

    allergies, meds, problems, immunizations, procedures, vitals, encounters, labs, imaging, careplans = \
        get_all_sections(patient_id)

    xml = build_ccd(
        patient_data,
        allergies, meds, problems, immunizations, procedures,
        vitals, encounters, labs, imaging, careplans
    )

    return Response(content=xml, media_type="application/xml")


# ---------------------------------------------------------------------
# 2️⃣ PRETTY PRINTED CCD
# ---------------------------------------------------------------------
@router.get("/{patient_id}/ccd/pretty", summary="Pretty-printed CCD XML")
def generate_pretty_ccd(patient_id: int):
    patient = get_patient(patient_id)
    if not patient:
        raise HTTPException(404, "Patient not found")

    patient_data = patient.model_dump()
    patient_data["name"] = f"{patient.first_name} {patient.last_name}"
    patient_data["dob"] = patient.dob or ""

    allergies, meds, problems, immunizations, procedures, vitals, encounters, labs, imaging, careplans = \
        get_all_sections(patient_id)

    xml = build_ccd(
        patient_data,
        allergies, meds, problems, immunizations, procedures,
        vitals, encounters, labs, imaging, careplans
    )

    pretty = pretty_xml(xml)
    return Response(content=pretty, media_type="application/xml")


# ---------------------------------------------------------------------
# 3️⃣ DOWNLOADABLE CCD FILE
# ---------------------------------------------------------------------
@router.get("/{patient_id}/ccd/download", summary="Download CCD as file")
def download_ccd(patient_id: int):
    patient = get_patient(patient_id)
    if not patient:
        raise HTTPException(404, "Patient not found")

    patient_data = patient.model_dump()
    patient_data["name"] = f"{patient.first_name} {patient.last_name}"
    patient_data["dob"] = patient.dob or ""

    allergies, meds, problems, immunizations, procedures, vitals, encounters, labs, imaging, careplans = \
        get_all_sections(patient_id)

    xml = build_ccd(
        patient_data,
        allergies, meds, problems, immunizations, procedures,
        vitals, encounters, labs, imaging, careplans
    )

    # temporary file
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".xml")
    tmp.write(xml.encode("utf-8"))
    tmp.close()

    filename = f"CCD-{patient_id}.xml"

    return FileResponse(tmp.name, media_type="application/xml", filename=filename)


# ---------------------------------------------------------------------
# 4️⃣ FHIR JSON VERSION OF CCD
# ---------------------------------------------------------------------
@router.get("/{patient_id}/ccd/fhir", summary="CCD in FHIR JSON Format")
def generate_fhir_ccd(patient_id: int):
    patient = get_patient(patient_id)
    if not patient:
        raise HTTPException(404, "Patient not found")

    patient_data = patient.model_dump()
    patient_data["name"] = f"{patient.first_name} {patient.last_name}"
    patient_data["dob"] = patient.dob or ""

    allergies, meds, problems, immunizations, procedures, vitals, encounters, labs, imaging, careplans = \
        get_all_sections(patient_id)

    bundle = convert_to_fhir(
        patient_data,
        allergies, meds, problems, immunizations, procedures,
        vitals, encounters, labs, imaging, careplans
    )

    return JSONResponse(content=bundle)