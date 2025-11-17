from fastapi import APIRouter, Depends, HTTPException
from ..auth import require_roles
from ..schemas_problems import ProblemCreate, ProblemUpdate
from ..crud_problems import (
    create_problem, get_problem, list_patient_problems,
    update_problem, delete_problem
)

router = APIRouter(prefix="/problems", tags=["Problem List"])


@router.post("/", dependencies=[Depends(require_roles("admin", "provider"))])
def create_problem_record(data: ProblemCreate):
    return create_problem(data)


@router.get("/{problem_id}")
def get_problem_record(problem_id: int):
    result = get_problem(problem_id)
    if not result:
        raise HTTPException(404, "Problem not found")
    return result


@router.get("/patient/{patient_id}")
def list_problems(patient_id: int):
    return list_patient_problems(patient_id)


@router.put("/{problem_id}", dependencies=[Depends(require_roles("admin", "provider"))])
def update_problem_record(problem_id: int, data: ProblemUpdate):
    return update_problem(problem_id, data)


@router.delete("/{problem_id}", dependencies=[Depends(require_roles("admin"))])
def delete_problem_record(problem_id: int):
    return delete_problem(problem_id)