from database import get_connection

conn = get_connection()
cur = conn.cursor()
cur.execute("DROP TABLE IF EXISTS patients")
conn.commit()
conn.close()

print("Patients table dropped successfully")
