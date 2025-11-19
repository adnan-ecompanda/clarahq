import sqlite3
from pathlib import Path
from typing import Any, Dict

DB_PATH = Path(__file__).resolve().parent.parent / "clarahq.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.close()


def dict_from_row(row: sqlite3.Row) -> Dict[str, Any]:
    return dict(row)