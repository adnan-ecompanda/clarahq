# reset_superbill_tables.py
from database import get_connection

conn = get_connection()
cur = conn.cursor()

print("Dropping superbill tables...")

# cur.execute("DROP TABLE IF EXISTS superbill_cpt_items")
# cur.execute("DROP TABLE IF EXISTS superbill_icd_items")
# cur.execute("DROP TABLE IF EXISTS superbills")
# cur.execute("DROP TABLE IF EXISTS claims")
cur.execute("DROP TABLE IF EXISTS eligibility_requests")

conn.commit()
conn.close()

print("DONE. Now restart your server to recreate tables.")