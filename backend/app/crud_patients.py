from typing import Optional, List

from .database import get_connection, dict_from_row
from . import schemas


def create_patient(data: schemas.PatientCreate) -> schemas.PatientOut:
    conn = get_connection()
    cur = conn.cursor()
    payload = data.model_dump()

    cur.execute(
        """
        INSERT INTO patients (
            mrn, external_id,
            first_name, middle_name, last_name, dob, gender, photo_url,
            phone_primary, phone_secondary, email,
            address_line1, address_line2, city, state, zip_code, country,
            emergency_contact_name, emergency_contact_relationship, emergency_contact_phone,
            insurance_provider, insurance_plan, insurance_member_id, insurance_group_number,
            insurance_effective_date, insurance_expiration_date,
            allergies, medications, notes,
            preferred_language, requires_interpreter, is_active
        )
        VALUES (
            :mrn, :external_id,
            :first_name, :middle_name, :last_name, :dob, :gender, :photo_url,
            :phone_primary, :phone_secondary, :email,
            :address_line1, :address_line2, :city, :state, :zip_code, :country,
            :emergency_contact_name, :emergency_contact_relationship, :emergency_contact_phone,
            :insurance_provider, :insurance_plan, :insurance_member_id, :insurance_group_number,
            :insurance_effective_date, :insurance_expiration_date,
            :allergies, :medications, :notes,
            :preferred_language, :requires_interpreter, :is_active
        )
        """,
        payload,
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()

    patient = get_patient(new_id)
    assert patient is not None
    return patient


def get_patient(patient_id: int) -> Optional[schemas.PatientOut]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return schemas.PatientOut(**dict_from_row(row))


def list_patients() -> List[schemas.PatientOut]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM patients ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return [schemas.PatientOut(**dict_from_row(r)) for r in rows]


def delete_patient(patient_id: int) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
    conn.commit()
    deleted = cur.rowcount > 0
    conn.close()
    return deleted