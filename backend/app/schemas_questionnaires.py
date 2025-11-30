# schemas_questionnaires.py

from pydantic import BaseModel
from typing import List, Optional


# -------------------------
# CREATE QUESTIONNAIRE
# -------------------------
class QuestionnaireCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None  # PHQ-9, GAD-7, Pain, Custom


# -------------------------
# ADD QUESTION
# -------------------------
class QuestionCreate(BaseModel):
    question_text: str
    question_type: str  # text, number, radio, checkbox
    options: Optional[List[str]] = None
    score_value: Optional[int] = None
    sort_order: int = 0


# -------------------------
# SUBMIT QUESTIONNAIRE
# -------------------------
class AnswerSubmit(BaseModel):
    question_id: int
    answer_text: Optional[str] = None
    answer_score: Optional[int] = None


# class QuestionnaireSubmit(BaseModel):
#     patient_id: int
#     encounter_id: int
#     answers: List[AnswerSubmit]
class QuestionnaireSubmit(BaseModel):
    patient_id: int
    encounter_id: int
    questionnaire_id: int
    answers: List[AnswerSubmit]