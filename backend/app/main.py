from fastapi import FastAPI

from .database import init_db
from .routers import patients as patients_router

# Make sure DB and tables exist on startup
init_db()

app = FastAPI(
    title="ClaraHQ Backend (Python 3.13 + SQLite)",
    version="0.1.0"
)


@app.get("/")
def root():
    return {"message": "ClaraHQ backend is running", "docs": "/docs"}


# Add patient routes
app.include_router(patients_router.router)