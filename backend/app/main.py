from fastapi import FastAPI

from .database import init_db
from .crud_user import init_user_table
from .crud_patient import init_patient_table
from .crud_encounter import init_encounter_table
from .crud_note import init_note_table
from .crud_order import init_order_table
from .crud_results import init_results_tables

from .routers import patients as patients_router
from .routers import users as users_router
from .routers import encounters as encounters_router
from .routers import notes as notes_router
from .routers import orders as orders_router
from .routers import results as results_router

# Create tables on startup
init_db()
init_user_table()
init_patient_table()
init_encounter_table()   # <-- REQUIRED
init_note_table()
init_order_table()
init_results_tables()

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