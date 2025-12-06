from fastapi import FastAPI

from .database import init_db
from .crud_user import init_user_table
from .crud_patient import init_patient_table
from .crud_encounter import init_encounter_table
from .crud_note import init_note_table
from .crud_order import init_order_table
from .crud_results import init_results_tables
from .crud_medication import init_medication_table
from .crud_allergies import init_allergy_table
from .crud_mar import init_mar_tables
from .crud_immunization import init_immunization_table
from .crud_problems import init_problem_table
from .crud_procedures import init_procedure_table
from .crud_careplans import init_careplan_table
from .crud_tasks import init_task_table
from .crud_documents import init_document_tables
from .crud_messages import init_message_tables
from .crud_referrals import init_referral_tables
from .crud_vitals import init_vitals_tables
from .crud_appointments import init_appointment_tables
from .crud_portal_messages import init_portal_message_tables
from .crud_notifications import init_notification_tables
from .crud_insurance import init_insurance_tables
from .audit import init_audit_table
from .crud_prescriptions import init_prescription_table
from .crud_claims import init_claim_tables
from .crud_scraper import init_scraper_tables
from .crud_billing import (
    init_superbill_table,
    init_superbill_cpt_table,
    init_superbill_icd_table
)
from .crud_eligibility import init_eligibility_tables
from .crud_pa import init_pa_tables
from .crud_templates import init_template_tables
from .crud_patient_portal import init_patient_portal_tables
from .crud_consent import init_consent_tables
from .crud_questionnaires import init_questionnaire_tables
from .crud_payments import init_payment_tables
from .crud_insurance_cards import init_insurance_card_tables

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
from .routers import portal_messages as portal_messages_router
from .routers import notifications as notifications_router
from .routers import insurance as insurance_router
from .routers import ccd as ccd_router
from .routers import avs as avs_router
from .routers import portal_auth as portal_auth_router
from .routers import telehealth as telehealth_router
from .routers import prescriptions as prescriptions_router
from .routers import insurance_eligibility as insurance_eligibility_router
from .routers import claims as claims_router
from .routers import eligibility as eligibility_router
from .routers import pa as pa_router
from .routers import scraper as scraper_router
from .routers import templates as templates_router
from .routers import patient_portal as patient_portal_router
from .routers import consent as consent_router
from .routers import questionnaires as questionnaires_router
from .routers import payments as payments_router
from .routers import insurance_cards as insurance_cards_router


# -----------------------------------------------------
# INIT DB TABLES
# -----------------------------------------------------

init_db()
init_user_table()
init_patient_table()
init_encounter_table()
init_note_table()
init_order_table()
init_results_tables()
init_medication_table()
init_allergy_table()
init_mar_tables()
init_immunization_table()
init_problem_table()
init_procedure_table()
init_careplan_table()
init_task_table()
init_document_tables()
init_message_tables()
init_referral_tables()
init_vitals_tables()
init_appointment_tables()
init_portal_message_tables()
init_notification_tables()
init_insurance_tables()
init_audit_table()
init_prescription_table()

# ❗ DO NOT CALL init_superbill_table() — IT NO LONGER EXISTS
init_superbill_cpt_table()
init_superbill_icd_table()
init_superbill_table()
init_claim_tables()
init_eligibility_tables()
init_pa_tables()
init_scraper_tables()
init_template_tables()

init_patient_portal_tables()
init_consent_tables()
init_questionnaire_tables()
init_payment_tables()
init_insurance_card_tables()

# -----------------------------------------------------
# FASTAPI INSTANCE
# -----------------------------------------------------

app = FastAPI(
    title="ClaraHQ Backend (Python 3.13 + SQLite)",
    version="0.2.0"
)

@app.get("/")
def root():
    return {"message": "ClaraHQ backend running", "docs": "/docs"}

# -----------------------------------------------------
# ROUTERS
# -----------------------------------------------------

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

# NEW NESTED SUPERBILL ROUTER
app.include_router(billing_router.router)
app.include_router(claims_router.router)

app.include_router(tasks_router.router)
# app.include_router(documents_router.router)
app.include_router(documents_router.router, prefix="/documents", tags=["Documents"])

app.include_router(messages_router.router)
app.include_router(referrals_router.router)
app.include_router(vitals_router.router)
app.include_router(appointments_router.router)
app.include_router(portal_messages_router.router)
app.include_router(notifications_router.router)
app.include_router(insurance_router.router)
app.include_router(ccd_router.router)
app.include_router(avs_router.router)
app.include_router(portal_auth_router.router)
app.include_router(telehealth_router.router)
app.include_router(prescriptions_router.router)
app.include_router(insurance_eligibility_router.router)
app.include_router(eligibility_router.router)
app.include_router(pa_router.router)
app.include_router(scraper_router.router)
app.include_router(templates_router.router)
app.include_router(patient_portal_router.router)
app.include_router(consent_router.router)
app.include_router(questionnaires_router.router)
app.include_router(payments_router.router)
app.include_router(insurance_cards_router.router)