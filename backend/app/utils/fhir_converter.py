from datetime import datetime


def convert_to_fhir(
    patient,
    allergies,
    meds,
    problems,
    immunizations,
    procedures,
    vitals,
    encounters,
    labs,
    imaging,
    careplans
):
    """
    Convert all CCD components into a full FHIR R4 Bundle.
    """

    bundle = {
        "resourceType": "Bundle",
        "type": "document",
        "id": f"CCD-FHIR-{patient['id']}",
        "timestamp": datetime.utcnow().isoformat(),
        "entry": []
    }

    # =====================================================================
    # PATIENT
    # =====================================================================
    patient_resource = {
        "resourceType": "Patient",
        "id": f"patient-{patient['id']}",
        "name": [{"text": patient["name"]}],
        "gender": patient.get("gender"),
        "birthDate": patient.get("dob", "") or None,
        "address": [
            {"text": patient.get("address_line1", "")}
        ]
    }

    bundle["entry"].append({"resource": patient_resource})


    # =====================================================================
    # ALLERGIES
    # =====================================================================
    for a in allergies:
        resource = {
            "resourceType": "AllergyIntolerance",
            "id": f"allergy-{a['id']}",
            "clinicalStatus": {"text": "active" if a.get("active") == 1 else "inactive"},
            "verificationStatus": {"text": "confirmed"},
            "type": "allergy",
            "criticality": a.get("severity"),
            "patient": {"reference": f"Patient/patient-{a['patient_id']}"},
            "code": {"text": a["allergen"]},
            "reaction": [{"description": a.get("reaction", "")}],
            "note": [{"text": a.get("notes", "")}]
        }
        bundle["entry"].append({"resource": resource})


    # =====================================================================
    # MEDICATIONS
    # Medication + MedicationStatement combo
    # =====================================================================
    for m in meds:

        # Medication resource
        medication_id = f"medication-{m['id']}"
        med_resource = {
            "resourceType": "Medication",
            "id": medication_id,
            "code": {"text": m["medication_name"]},
            "form": {"text": m.get("route", "")},
        }

        bundle["entry"].append({"resource": med_resource})

        # MedicationStatement resource
        statement_resource = {
            "resourceType": "MedicationStatement",
            "id": f"medstmt-{m['id']}",
            "status": m.get("status", "active"),
            "medicationReference": {"reference": f"Medication/{medication_id}"},
            "subject": {"reference": f"Patient/patient-{m['patient_id']}"},
            "dosage": [{
                "text": f"{m.get('strength','')} {m.get('frequency','')}",
                "route": {"text": m.get("route")},
            }],
            "note": [{"text": m.get("instructions", "")}]
        }

        bundle["entry"].append({"resource": statement_resource})


    # =====================================================================
    # PROBLEMS (Conditions)
    # =====================================================================
    for p in problems:
        resource = {
            "resourceType": "Condition",
            "id": f"problem-{p['id']}",
            "clinicalStatus": {"text": p.get("status", "active")},
            "code": {"text": p["description"]},
            "subject": {"reference": f"Patient/patient-{p['patient_id']}"},
            "onsetDateTime": p.get("onset_date"),
            "abatementDateTime": p.get("resolved_date"),
            "note": [{"text": p.get("notes", "")}]
        }
        bundle["entry"].append({"resource": resource})


    # =====================================================================
    # IMMUNIZATIONS
    # =====================================================================
    for im in immunizations:
        resource = {
            "resourceType": "Immunization",
            "id": f"immunization-{im['id']}",
            "status": "completed",
            "vaccineCode": {"text": im.get("vaccine_name")},
            "patient": {"reference": f"Patient/patient-{im['patient_id']}"},
            "occurrenceDateTime": im.get("administered_date"),
            "lotNumber": im.get("lot_number"),
            "site": {"text": im.get("site")},
            "route": {"text": im.get("route")},
            "note": [{"text": im.get("notes", "")}]
        }
        bundle["entry"].append({"resource": resource})


    # =====================================================================
    # PROCEDURES
    # =====================================================================
    for pr in procedures:
        resource = {
            "resourceType": "Procedure",
            "id": f"procedure-{pr['id']}",
            "status": "completed",
            "code": {"text": pr.get("name")},
            "subject": {"reference": f"Patient/patient-{pr['patient_id']}"},
            "performedDateTime": pr.get("procedure_date"),
            "note": [{"text": pr.get("notes", "")}]
        }
        bundle["entry"].append({"resource": resource})


    # =====================================================================
    # ENCOUNTERS
    # =====================================================================
    for e in encounters:
        resource = {
            "resourceType": "Encounter",
            "id": f"encounter-{e['id']}",
            "status": "finished",
            "class": {"code": "AMB"},
            "type": [{"text": e.get("visit_type")}],
            "subject": {"reference": f"Patient/patient-{e['patient_id']}"},
            "period": {
                "start": e.get("visit_date"),
                "end": e.get("visit_date")
            },
            "reasonCode": [{"text": e.get("chief_complaint")}],
            "note": [{"text": e.get("plan")}]
        }
        bundle["entry"].append({"resource": resource})


    # =====================================================================
    # VITAL SIGNS → Observation
    # =====================================================================
    for v in vitals:
        for code, value in {
            "Blood Pressure": v.get("bp_systolic"),
            "Heart Rate": v.get("heart_rate"),
            "Respiratory Rate": v.get("respiratory_rate"),
            "Temperature": v.get("temperature"),
            "SpO2": v.get("spo2"),
            "Weight": v.get("weight"),
            "Height": v.get("height"),
            "BMI": v.get("bmi")
        }.items():

            if value is None:
                continue

            resource = {
                "resourceType": "Observation",
                "id": f"vital-{v['id']}-{code.replace(' ', '')}",
                "status": "final",
                "category": [{"text": "vital-signs"}],
                "code": {"text": code},
                "subject": {"reference": f"Patient/patient-{v['patient_id']}"},
                "effectiveDateTime": v.get("taken_at"),
                "valueString": str(value),
                "note": [{"text": v.get("notes", "")}]
            }

            bundle["entry"].append({"resource": resource})


    # =====================================================================
    # LABS → Observation
    # =====================================================================
    for lab in labs:
        resource = {
            "resourceType": "Observation",
            "id": f"lab-{lab['id']}",
            "status": "final",
            "category": [{"text": "laboratory"}],
            "code": {"text": lab.get("test_name")},
            "subject": {"reference": f"Patient/patient-{lab['patient_id']}"},
            "valueString": f"{lab.get('value')} {lab.get('unit','')}",
            "referenceRange": [{"text": lab.get("reference_range")}],
            "interpretation": [{"text": lab.get("abnormal_flag")}],
            "effectiveDateTime": lab.get("result_date"),
            "note": [{"text": lab.get("notes", "")}]
        }
        bundle["entry"].append({"resource": resource})


    # =====================================================================
    # IMAGING → DiagnosticReport
    # =====================================================================
    for img in imaging:
        resource = {
            "resourceType": "DiagnosticReport",
            "id": f"imaging-{img['id']}",
            "status": "final",
            "category": [{"text": "imaging"}],
            "code": {"text": img.get("modality")},
            "subject": {"reference": f"Patient/patient-{img['patient_id']}"},
            "effectiveDateTime": img.get("result_date"),
            "conclusion": img.get("impression"),
            "result": [],
            "note": [{"text": img.get("findings", "")}]
        }
        bundle["entry"].append({"resource": resource})


    # =====================================================================
    # CARE PLANS
    # =====================================================================
    for cp in careplans:
        resource = {
            "resourceType": "CarePlan",
            "id": f"careplan-{cp['id']}",
            "status": cp.get("status", "active"),
            "intent": "plan",
            "title": cp.get("title"),
            "subject": {"reference": f"Patient/patient-{cp['patient_id']}"},
            "description": cp.get("diagnosis"),
            "period": {
                "start": cp.get("start_date"),
                "end": cp.get("review_date")
            },
            "goal": [{"description": cp.get("goals")}],
            "activity": [{"detail": {"description": cp.get("interventions")}}],
            "note": [{"text": cp.get("actual_outcomes","")}]
        }
        bundle["entry"].append({"resource": resource})


    return bundle