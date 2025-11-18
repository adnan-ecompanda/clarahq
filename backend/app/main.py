from fastapi import FastAPI

from .database import init_db
from .crud_user import init_user_table
from .crud_patient import init_patient_table
from .crud_encounter import init_encounter_table
from .crud_note import init_note_table
from .crud_order import init_order_table
from .crud_results import init_results_tables
from .crud_results import init_imaging_attachments_table
from .crud_medication import init_medication_table
from .crud_allergies import init_allergy_table
from .crud_mar import init_mar_tables
from .crud_immunization import init_immunization_table
from .crud_problems import init_problem_table
from .crud_procedures import init_procedure_table
from .crud_careplans import init_careplan_table
from .crud_billing import init_billing_tables
from .crud_tasks import init_task_table
from .crud_documents import init_document_tables
from .crud_messages import init_message_tables
from .crud_referrals import init_referral_tables
from .crud_vitals import init_vitals_tables
from .crud_appointments import init_appointment_tables

from .routers import patients as patients_router
from .routers import users as users_router
from .routers import encounters as encounters_router
from .routers import notes as notes_router
from .routers import orders as orders_router
from .routers import results as results_router
from .routers import medications as medications_router
from .routers import allergies as allergies_router
from .routers import mar as mar_router
from .routers import immunizations as immunization_router
from .routers import problems as problems_router
from .routers import procedures as procedures_router
from .routers import careplans as careplans_router
from .routers import billing as billing_router
from .routers import tasks as tasks_router
from .routers import documents as documents_router
from .routers import messages as messages_router
from .routers import referrals as referrals_router
from .routers import vitals as vitals_router
from .routers import appointments as appointments_router

# Create tables on startup
init_db()
init_user_table()
init_patient_table()
init_encounter_table()
init_note_table()
init_order_table()
init_results_tables()
init_imaging_attachments_table()
init_medication_table()
init_allergy_table()
init_mar_tables()
init_immunization_table()
init_problem_table()
init_procedure_table()
init_careplan_table()
init_billing_tables()
init_task_table()
init_document_tables()
init_message_tables()
init_referral_tables()
init_vitals_tables()
init_appointment_tables()

app = FastAPI(
    title="ClaraHQ Backend (Python 3.13 + SQLite)",
    version="0.2.0"
)

@app.get("/")
def root():
    return {"message": "ClaraHQ backend running", "docs": "/docs"}

# Routers
app.include_router(users_router.router)
app.include_router(patients_router.router)
app.include_router(encounters_router.router)
app.include_router(notes_router.router)
app.include_router(orders_router.router)
app.include_router(results_router.router)
app.include_router(medications_router.router)
app.include_router(allergies_router.router)
app.include_router(mar_router.router)
app.include_router(immunization_router.router)
app.include_router(problems_router.router)
app.include_router(procedures_router.router)
app.include_router(careplans_router.router)
app.include_router(billing_router.router)
app.include_router(tasks_router.router)
app.include_router(documents_router.router)
app.include_router(messages_router.router)
app.include_router(referrals_router.router)
app.include_router(vitals_router.router)
app.include_router(appointments_router.router)