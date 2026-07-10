from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from backend.schemas import AssessmentResponse

DB_PATH = Path("data/greysignal.sqlite")


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                country TEXT NOT NULL,
                sector TEXT NOT NULL,
                overall_score REAL NOT NULL,
                rating TEXT NOT NULL,
                generated_at TEXT NOT NULL,
                payload TEXT NOT NULL
            )
            """
        )


def save_assessment(response: AssessmentResponse) -> None:
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO assessments (country, sector, overall_score, rating, generated_at, payload)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                response.country,
                response.sector,
                response.overall_score,
                response.rating,
                response.generated_at,
                response.model_dump_json(),
            ),
        )
