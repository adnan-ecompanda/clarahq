from .database import get_connection, dict_from_row
from .utils.telehealth import generate_telehealth_url


def create_or_update_telehealth_link(appointment_id: int):
    url, meeting_id = generate_telehealth_url()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE appointments
        SET telehealth_url = ?, updated_at = datetime('now')
        WHERE id = ?
    """, (url, appointment_id))

    conn.commit()
    conn.close()

    return {"appointment_id": appointment_id, "telehealth_url": url}


def get_telehealth_link(appointment_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT telehealth_url FROM appointments WHERE id = ?", (appointment_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    return dict_from_row(row)