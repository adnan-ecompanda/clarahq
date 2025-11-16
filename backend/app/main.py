from fastapi import FastAPI

from .database import init_db
from .crud_user import init_user_table
from .routers import patients as patients_router
from .routers import users as users_router

# Create tables
init_db()
init_user_table()

app = FastAPI(
    title="ClaraHQ Backend (Python 3.13 + SQLite)",
    version="0.2.0"
)


@app.get("/")
def root():
    return {"message": "ClaraHQ backend running", "docs": "/docs"}


app.include_router(users_router.router)
app.include_router(patients_router.router)