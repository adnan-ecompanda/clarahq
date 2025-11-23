from typing import Dict, List, Any
from app.database import get_connection, dict_from_row


def load_superbill(sb_id: int) -> Dict[str, Any]:
    conn = get_connection()
    cur = conn.cursor()

    # Load superbill
    cur.execute("SELECT * FROM superbills WHERE id = ?", (sb_id,))
    sb = cur.fetchone()
    if not sb:
        return None
    sb = dict_from_row(sb)

    # Load CPT items
    cur.execute("""
        SELECT * FROM superbill_cpt_items WHERE superbill_id = ?
    """, (sb_id,))
    cpt_items = [dict_from_row(r) for r in cur.fetchall()]

    # Load ICD items
    cur.execute("""
        SELECT * FROM superbill_icd_items WHERE superbill_id = ?
    """, (sb_id,))
    icd_items = [dict_from_row(r) for r in cur.fetchall()]

    # Load encounter
    cur.execute("SELECT * FROM encounters WHERE id = ?", (sb["encounter_id"],))
    encounter = dict_from_row(cur.fetchone())

    # Load patient
    cur.execute("SELECT * FROM patients WHERE id = ?", (encounter["patient_id"],))
    patient = dict_from_row(cur.fetchone())

    conn.close()

    return {
        "superbill": sb,
        "cpt": cpt_items,
        "icd": icd_items,
        "encounter": encounter,
        "patient": patient
    }

def generate_claim_json(bundle: Dict[str, Any]) -> Dict[str, Any]:
    sb = bundle["superbill"]
    patient = bundle["patient"]
    encounter = bundle["encounter"]

    return {
        "claim_id": sb["id"],
        "patient": {
            "id": patient["id"],
            "name": f"{patient['first_name']} {patient['last_name']}",
            "dob": patient["dob"],
            "gender": patient["gender"],
            "phone": patient["phone_primary"],
            "address": {
                "line1": patient["address_line1"],
                "line2": patient["address_line2"],
                "city": patient["city"],
                "state": patient["state"],
                "zip": patient["zip_code"],
            }
        },

        "encounter": {
            "encounter_id": encounter["id"],
            "visit_date": encounter["visit_date"],
            "provider": encounter["provider_name"],
            "location": encounter["location"],
            "chief_complaint": encounter["chief_complaint"],
        },

        "diagnoses": bundle["icd"],
        "procedures": bundle["cpt"],

        "total_charge": sum([
            float(item["amount"] or 0) * (item["units"] or 1)
            for item in bundle["cpt"]
        ])
    }

def generate_x12_837p(bundle: Dict[str, Any]) -> str:
    patient = bundle["patient"]
    sb = bundle["superbill"]
    encounter = bundle["encounter"]

    segments = []

    segments.append("ISA*00* *00* *ZZ*SENDERID      *ZZ*RECEIVERID    *240101*1253*^*00501*000000905*0*T*:~")
    segments.append("GS*HC*SENDERID*RECEIVERID*20240101*1253*1*X*005010X222A1~")
    segments.append("ST*837*0001*005010X222A1~")

    # Patient Loop
    segments.append(f"NM1*IL*1*{patient['last_name']}*{patient['first_name']}****MI*{sb['id']}~")

    # Diagnoses
    for idx, icd in enumerate(bundle["icd"], start=1):
        segments.append(f"HI*ABK:{icd['icd_code']}~")

    # CPT lines
    for cpt in bundle["cpt"]:
        charge = float(cpt["amount"] or 0) * (cpt["units"] or 1)
        segments.append(f"SV1*HC:{cpt['cpt_code']}*{charge:.2f}*UN*{cpt['units']}***1~")

    segments.append("SE*23*0001~")
    segments.append("GE*1*1~")
    segments.append("IEA*1*000000905~")

    return "\n".join(segments)