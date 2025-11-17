from fastapi import APIRouter, HTTPException, Depends, Query
from ..auth import require_roles, get_current_user
from ..schemas_tasks import TaskCreate, TaskUpdate
from ..crud_tasks import (
    create_task, get_task, list_tasks,
    update_task, delete_task
)

router = APIRouter(prefix="/tasks", tags=["Tasks"])


# ------------------- CREATE TASK -------------------

@router.post("/", dependencies=[Depends(require_roles("admin", "provider"))])
def create_new_task(data: TaskCreate, current_user=Depends(get_current_user)):
    data.created_by = current_user["id"]
    return create_task(data)


# ------------------- LIST TASKS -------------------

@router.get("/")
def all_tasks(status: str | None = Query(None)):
    return list_tasks(status)


# ------------------- GET SINGLE TASK -------------------

@router.get("/{task_id}")
def get_single_task(task_id: int):
    rec = get_task(task_id)
    if not rec:
        raise HTTPException(404, "Task not found")
    return rec


# ------------------- UPDATE TASK -------------------

@router.put("/{task_id}", dependencies=[Depends(require_roles("admin", "provider", "staff"))])
def modify_task(task_id: int, data: TaskUpdate):
    return update_task(task_id, data)


# ------------------- DELETE TASK -------------------

@router.delete("/{task_id}", dependencies=[Depends(require_roles("admin"))])
def remove_task(task_id: int):
    return delete_task(task_id)