import sqlite3
import json
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).parent / "passages.db"


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS passages (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT    NOT NULL,
            text        TEXT    NOT NULL,
            category    TEXT    NOT NULL,
            source      TEXT    NOT NULL,
            source_url  TEXT,
            scraped_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(title, source)
        );

        CREATE TABLE IF NOT EXISTS questions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            passage_id  INTEGER NOT NULL REFERENCES passages(id) ON DELETE CASCADE,
            seq         INTEGER NOT NULL,
            text        TEXT    NOT NULL,
            options     TEXT    NOT NULL,
            correct     INTEGER NOT NULL,
            explanation TEXT    NOT NULL DEFAULT ''
        );
    """)
    conn.commit()
    conn.close()


def upsert_passage(title: str, text: str, category: str,
                   source: str, source_url: str,
                   questions: list) -> int:
    """Insert passage (skip if duplicate title+source). Returns passage id."""
    conn = get_conn()
    try:
        cur = conn.execute(
            """INSERT OR IGNORE INTO passages (title, text, category, source, source_url)
               VALUES (?, ?, ?, ?, ?)""",
            (title, text, category, source, source_url)
        )
        if cur.lastrowid == 0:
            # Already exists — fetch the id
            row = conn.execute(
                "SELECT id FROM passages WHERE title=? AND source=?",
                (title, source)
            ).fetchone()
            passage_id = row["id"]
        else:
            passage_id = cur.lastrowid

        # Insert questions (skip if passage already had questions)
        existing = conn.execute(
            "SELECT COUNT(*) FROM questions WHERE passage_id=?", (passage_id,)
        ).fetchone()[0]
        if existing == 0:
            for i, q in enumerate(questions):
                conn.execute(
                    """INSERT INTO questions (passage_id, seq, text, options, correct, explanation)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (passage_id, i, q["text"], json.dumps(q["options"]),
                     q["correct"], q.get("explanation", ""))
                )
        conn.commit()
        return passage_id
    finally:
        conn.close()


def get_passages(category: str = "all", limit: int = 50) -> list:
    conn = get_conn()
    try:
        if category == "all":
            rows = conn.execute(
                """SELECT p.id, p.title, p.category, p.source, p.source_url,
                          COUNT(q.id) as question_count
                   FROM passages p
                   LEFT JOIN questions q ON q.passage_id = p.id
                   GROUP BY p.id
                   ORDER BY p.scraped_at DESC
                   LIMIT ?""", (limit,)
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT p.id, p.title, p.category, p.source, p.source_url,
                          COUNT(q.id) as question_count
                   FROM passages p
                   LEFT JOIN questions q ON q.passage_id = p.id
                   WHERE p.category = ?
                   GROUP BY p.id
                   ORDER BY p.scraped_at DESC
                   LIMIT ?""", (category, limit)
            ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_passage_by_id(passage_id: int) -> Optional[dict]:
    conn = get_conn()
    try:
        p = conn.execute(
            "SELECT * FROM passages WHERE id=?", (passage_id,)
        ).fetchone()
        if not p:
            return None
        questions = conn.execute(
            "SELECT * FROM questions WHERE passage_id=? ORDER BY seq",
            (passage_id,)
        ).fetchall()
        result = dict(p)
        result["questions"] = [
            {
                "id": q["id"],
                "text": q["text"],
                "options": json.loads(q["options"]),
                "correct": q["correct"],
                "explanation": q["explanation"],
            }
            for q in questions
        ]
        return result
    finally:
        conn.close()


def get_random_passage(category: str = "all") -> Optional[dict]:
    conn = get_conn()
    try:
        if category == "all":
            row = conn.execute(
                "SELECT id FROM passages ORDER BY RANDOM() LIMIT 1"
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT id FROM passages WHERE category=? ORDER BY RANDOM() LIMIT 1",
                (category,)
            ).fetchone()
        if not row:
            return None
        return get_passage_by_id(row["id"])
    finally:
        conn.close()


def count_passages() -> dict:
    conn = get_conn()
    try:
        total = conn.execute("SELECT COUNT(*) FROM passages").fetchone()[0]
        by_cat = conn.execute(
            "SELECT category, COUNT(*) as n FROM passages GROUP BY category"
        ).fetchall()
        return {"total": total, "by_category": {r["category"]: r["n"] for r in by_cat}}
    finally:
        conn.close()
