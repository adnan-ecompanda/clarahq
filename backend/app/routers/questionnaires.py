# routers/questionnaires.py

from fastapi import APIRouter, HTTPException, Depends
from typing import List

from ..auth import get_current_user
from ..crud_questionnaires import (
    create_questionnaire,
    add_question,
    get_questionnaire,
    submit_questionnaire,
    get_submission
)
from ..schemas_questionnaires import (
    QuestionnaireCreate,
    QuestionCreate,
    QuestionnaireSubmit,
)

router = APIRouter(
    prefix="/questionnaires",
    tags=["Questionnaires"]
)


# ---------------------------------------------------------
# CREATE QUESTIONNAIRE
# ---------------------------------------------------------
@router.post("/", summary="Create a new questionnaire")
def create_questionnaire_api(
    payload: QuestionnaireCreate,
    current_user=Depends(get_current_user)
):
    return create_questionnaire(
        name=payload.name,
        description=payload.description,
        category=payload.category,
        created_by=current_user["id"]
    )


# ---------------------------------------------------------
# ADD QUESTION TO QUESTIONNAIRE
# ---------------------------------------------------------
@router.post("/{questionnaire_id}/questions", summary="Add question to questionnaire")
def add_question_api(
    questionnaire_id: int,
    payload: QuestionCreate,
    current_user=Depends(get_current_user)
):
    return add_question(
        questionnaire_id=questionnaire_id,
        question_text=payload.question_text,
        question_type=payload.question_type,
        options=payload.options,
        score_value=payload.score_value,
        sort_order=payload.sort_order
    )


# ---------------------------------------------------------
# GET QUESTIONNAIRE WITH QUESTIONS
# ---------------------------------------------------------
@router.get("/{questionnaire_id}", summary="Get questionnaire with all questions")
def get_questionnaire_api(questionnaire_id: int):
    data = get_questionnaire(questionnaire_id)
    if not data:
        raise HTTPException(404, "Questionnaire not found")
    return data


# ---------------------------------------------------------
# SUBMIT QUESTIONNAIRE
# ---------------------------------------------------------
@router.post("/{questionnaire_id}/submit", summary="Submit a completed questionnaire")
def submit_questionnaire_api(
    questionnaire_id: int,
    payload: QuestionnaireSubmit
):
    result = submit_questionnaire(
        questionnaire_id=questionnaire_id,
        patient_id=payload.patient_id,
        encounter_id=payload.encounter_id,
        answers_list=payload.answers
    )
    return result


# ---------------------------------------------------------
# VIEW SUBMISSION
# ---------------------------------------------------------
@router.get("/submissions/{submission_id}", summary="Get submitted questionnaire")
def get_submission_api(submission_id: int):
    data = get_submission(submission_id)
    if not data:
        raise HTTPException(404, "Submission not found")
    return data