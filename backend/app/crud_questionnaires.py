# crud_questionnaires.py
import json
import sqlite3
from datetime import datetime
from .database import get_connection

def init_questionnaire_tables():
    conn = get_connection()
    cur = conn.cursor()

    # -------------------------------
    # 1) Main Questionnaire Metadata
    # -------------------------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS questionnaires (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        category TEXT,                 -- PHQ-9, GAD-7, Pain, Custom, etc.
        is_published INTEGER DEFAULT 0,
        created_by INTEGER,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # -------------------------------
    # 2) Questions for Each Form
    # -------------------------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS questionnaire_questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        questionnaire_id INTEGER NOT NULL,
        question_text TEXT NOT NULL,
        question_type TEXT NOT NULL,   -- text, number, choice, multi-choice, scale
        options TEXT,                  -- JSON string for multiple-choice options
        score_value INTEGER,           -- For scoring systems (PHQ-9 = 0–3)
        sort_order INTEGER DEFAULT 0,
        FOREIGN KEY(questionnaire_id) REFERENCES questionnaires(id)
    )
    """)

    # ----------------------------------------------------
    # 3) Patient Submission (one record per filled form)
    # ----------------------------------------------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS questionnaire_submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        questionnaire_id INTEGER NOT NULL,
        patient_id INTEGER NOT NULL,
        encounter_id INTEGER,          -- optional: link to an encounter
        submitted_at TEXT DEFAULT CURRENT_TIMESTAMP,
        total_score INTEGER,           -- auto-calculated for PHQ-9 / GAD-7
        severity TEXT,                 -- auto classification
        FOREIGN KEY(questionnaire_id) REFERENCES questionnaires(id)
    )
    """)

    # ----------------------------------------------------
    # 4) Answers for each question inside each submission
    # ----------------------------------------------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS questionnaire_answers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        submission_id INTEGER NOT NULL,
        questionnaire_id INTEGER NOT NULL,
        answer_text TEXT,
        answer_score INTEGER,
        FOREIGN KEY(submission_id) REFERENCES questionnaire_submissions(id),
        FOREIGN KEY(questionnaire_id) REFERENCES questionnaire_questions(id)
    )
    """)

    conn.commit()
# -------------------------------------------------------
# CREATE QUESTIONNAIRE
# -------------------------------------------------------
def create_questionnaire(name, description=None, category=None, created_by=None):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO questionnaires (name, description, category, created_by)
        VALUES (?, ?, ?, ?)
    """, (name, description, category, created_by))

    conn.commit()
    return {"questionnaire_id": cur.lastrowid}


# -------------------------------------------------------
# ADD QUESTION TO QUESTIONNAIRE
# -------------------------------------------------------
def add_question(questionnaire_id, question_text, question_type, options=None, score_value=None, sort_order=0):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO questionnaire_questions
        (questionnaire_id, question_text, question_type, options, score_value, sort_order)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        questionnaire_id,
        question_text,
        question_type,
        json.dumps(options) if options else None,
        score_value,
        sort_order
    ))

    conn.commit()
    return {"questionnaire_id": cur.lastrowid}


# -------------------------------------------------------
# GET QUESTIONNAIRE WITH QUESTIONS
# -------------------------------------------------------
def get_questionnaire(questionnaire_id):
    conn = get_connection()
    cur = conn.cursor()

    # Questionnaire
    cur.execute("SELECT * FROM questionnaires WHERE id = ?", (questionnaire_id,))
    q = cur.fetchone()
    if not q:
        return None

    q_keys = ["id", "name", "description", "category", "is_published",
              "created_by", "created_at"]
    questionnaire = dict(zip(q_keys, q))

    # Questions
    cur.execute("""
        SELECT id, question_text, question_type, options, score_value, sort_order
        FROM questionnaire_questions
        WHERE questionnaire_id = ?
        ORDER BY sort_order ASC
    """, (questionnaire_id,))

    questions = []
    for row in cur.fetchall():
        questions.append({
            "id": row[0],
            "question_text": row[1],
            "question_type": row[2],
            "options": json.loads(row[3]) if row[3] else None,
            "score_value": row[4],
            "sort_order": row[5]
        })

    questionnaire["questions"] = questions
    return questionnaire


# -------------------------------------------------------
# SCORING LOGIC (PHQ-9, GAD-7, Pain Scale)
# -------------------------------------------------------
def calculate_score(category, answers):
    """
    Supports both:
    - dict values  → a["answer_score"]
    - Pydantic objects → a.answer_score
    """

    def get(a, key):
        """Safe getter for dict OR Pydantic objects"""
        if isinstance(a, dict):
            return a.get(key)
        return getattr(a, key, None)

    # -----------------------------
    # PHQ-9
    # -----------------------------
    if category in ["PHQ-9", "PHQ9"]:
        total = sum((get(a, "answer_score") or 0) for a in answers)

        if total <= 4:
            severity = "Minimal"
        elif total <= 9:
            severity = "Mild"
        elif total <= 14:
            severity = "Moderate"
        elif total <= 19:
            severity = "Moderately Severe"
        else:
            severity = "Severe"

        return total, severity

    # -----------------------------
    # GAD-7
    # -----------------------------
    if category in ["GAD-7", "GAD7"]:
        total = sum((get(a, "answer_score") or 0) for a in answers)

        if total <= 4:
            severity = "Minimal"
        elif total <= 9:
            severity = "Mild"
        elif total <= 14:
            severity = "Moderate"
        else:
            severity = "Severe"

        return total, severity

    # -----------------------------
    # Pain Scale 0–10
    # -----------------------------
    if category in ["Pain", "Pain Scale", "NRS"]:
        raw = get(answers[0], "answer_text") or "0"

        try:
            score = int(raw)
        except:
            score = 0

        if score <= 3:
            sev = "Mild"
        elif score <= 6:
            sev = "Moderate"
        else:
            sev = "Severe"

        return score, sev

    # -----------------------------
    # Default
    # -----------------------------
    return None, None


# -------------------------------------------------------
# SUBMIT QUESTIONNAIRE (SAVE ANSWERS + SCORING)
# -------------------------------------------------------
def submit_questionnaire(questionnaire_id, patient_id, encounter_id, answers_list):
    """
    answers_list = [
        {"questionnaire_id": 1, "answer_text": "Nearly every day", "answer_score": 3},
        {"questionnaire_id": 2, "answer_text": "Not at all", "answer_score": 0},
        ...
    ]
    """

    questionnaire = get_questionnaire(questionnaire_id)
    if not questionnaire:
        return {"error": "Questionnaire not found"}

    category = questionnaire["category"]

    total_score, severity = calculate_score(category, answers_list)

    conn = get_connection()
    cur = conn.cursor()

    # Insert submission record
    cur.execute("""
        INSERT INTO questionnaire_submissions
        (questionnaire_id, patient_id, encounter_id, total_score, severity)
        VALUES (?, ?, ?, ?, ?)
    """, (
        questionnaire_id,
        patient_id,
        encounter_id,
        total_score,
        severity
    ))

    submission_id = cur.lastrowid

    # Insert answers
    for item in answers_list:
        qid = item.question_id
        aval = item.answer_text
        ascore = item.answer_score

        cur.execute("""
            INSERT INTO questionnaire_answers
            (submission_id, questionnaire_id, answer_text, answer_score)
            VALUES (?, ?, ?, ?)
        """, (
            submission_id,
            qid,
            aval,
            ascore
        ))

    conn.commit()

    return {
        "submission_id": submission_id,
        "total_score": total_score,
        "severity": severity
    }


# -------------------------------------------------------
# GET SUBMISSION DETAILS
# -------------------------------------------------------
def get_submission(submission_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT questionnaire_id, patient_id, encounter_id,
               submitted_at, total_score, severity
        FROM questionnaire_submissions
        WHERE id = ?
    """, (submission_id,))

    row = cur.fetchone()
    if not row:
        return None

    submission = {
        "questionnaire_id": row[0],
        "patient_id": row[1],
        "encounter_id": row[2],
        "submitted_at": row[3],
        "total_score": row[4],
        "severity": row[5]
    }

    # Answers
    cur.execute("""
        SELECT questionnaire_id, answer_text, answer_score
        FROM questionnaire_answers
        WHERE submission_id = ?
    """, (submission_id,))

    submission["answers"] = [
        {
            "questionnaire_id": r[0],
            "answer_text": r[1],
            "answer_score": r[2]
        }
        for r in cur.fetchall()
    ]

    return submission