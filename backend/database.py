import json
import os
import psycopg2
import psycopg2.extras
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set.")


def get_conn():
    return psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS passages (
            id          SERIAL PRIMARY KEY,
            title       TEXT    NOT NULL,
            text        TEXT    NOT NULL,
            category    TEXT    NOT NULL,
            source      TEXT    NOT NULL,
            source_url  TEXT,
            scraped_at  TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(title, source)
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id          SERIAL PRIMARY KEY,
            passage_id  INTEGER NOT NULL REFERENCES passages(id) ON DELETE CASCADE,
            seq         INTEGER NOT NULL,
            text        TEXT    NOT NULL,
            options     JSONB   NOT NULL,
            correct     INTEGER NOT NULL,
            explanation TEXT    NOT NULL DEFAULT ''
        );
    """)
    conn.commit()
    cur.close()
    conn.close()


def upsert_passage(title: str, text: str, category: str,
                   source: str, source_url: str, questions: list) -> Optional[int]:
    """Insert passage (skip if duplicate title+source). Returns passage id."""
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            """INSERT INTO passages (title, text, category, source, source_url)
               VALUES (%s, %s, %s, %s, %s)
               ON CONFLICT (title, source) DO NOTHING
               RETURNING id""",
            (title, text, category, source, source_url)
        )
        row = cur.fetchone()
        if row:
            passage_id = row["id"]
        else:
            cur.execute(
                "SELECT id FROM passages WHERE title=%s AND source=%s",
                (title, source)
            )
            passage_id = cur.fetchone()["id"]

        # Only insert questions if not already present
        cur.execute("SELECT COUNT(*) as n FROM questions WHERE passage_id=%s", (passage_id,))
        if cur.fetchone()["n"] == 0:
            for i, q in enumerate(questions):
                cur.execute(
                    """INSERT INTO questions (passage_id, seq, text, options, correct, explanation)
                       VALUES (%s, %s, %s, %s, %s, %s)""",
                    (passage_id, i, q["text"], json.dumps(q["options"]),
                     q["correct"], q.get("explanation", ""))
                )
        conn.commit()
        return passage_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()


def get_passages(category: str = "all", limit: int = 50) -> list:
    conn = get_conn()
    cur = conn.cursor()
    try:
        if category == "all":
            cur.execute(
                """SELECT p.id, p.title, p.category, p.source, p.source_url,
                          COUNT(q.id) AS question_count
                   FROM passages p
                   LEFT JOIN questions q ON q.passage_id = p.id
                   GROUP BY p.id
                   ORDER BY p.scraped_at DESC
                   LIMIT %s""",
                (limit,)
            )
        else:
            cur.execute(
                """SELECT p.id, p.title, p.category, p.source, p.source_url,
                          COUNT(q.id) AS question_count
                   FROM passages p
                   LEFT JOIN questions q ON q.passage_id = p.id
                   WHERE p.category = %s
                   GROUP BY p.id
                   ORDER BY p.scraped_at DESC
                   LIMIT %s""",
                (category, limit)
            )
        return [dict(r) for r in cur.fetchall()]
    finally:
        cur.close()
        conn.close()


def get_passage_by_id(passage_id: int) -> Optional[dict]:
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM passages WHERE id=%s", (passage_id,))
        p = cur.fetchone()
        if not p:
            return None
        cur.execute(
            "SELECT * FROM questions WHERE passage_id=%s ORDER BY seq",
            (passage_id,)
        )
        questions = cur.fetchall()
        result = dict(p)
        result["questions"] = [
            {
                "id": q["id"],
                "text": q["text"],
                "options": q["options"] if isinstance(q["options"], list) else json.loads(q["options"]),
                "correct": q["correct"],
                "explanation": q["explanation"],
            }
            for q in questions
        ]
        return result
    finally:
        cur.close()
        conn.close()


def get_random_passage(category: str = "all") -> Optional[dict]:
    conn = get_conn()
    cur = conn.cursor()
    try:
        if category == "all":
            cur.execute("SELECT id FROM passages ORDER BY RANDOM() LIMIT 1")
        else:
            cur.execute(
                "SELECT id FROM passages WHERE category=%s ORDER BY RANDOM() LIMIT 1",
                (category,)
            )
        row = cur.fetchone()
        if not row:
            return None
        return get_passage_by_id(row["id"])
    finally:
        cur.close()
        conn.close()


def count_passages() -> dict:
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) AS n FROM passages")
        total = cur.fetchone()["n"]
        cur.execute("SELECT category, COUNT(*) AS n FROM passages GROUP BY category")
        by_cat = {r["category"]: r["n"] for r in cur.fetchall()}
        return {"total": total, "by_category": by_cat}
    finally:
        cur.close()
        conn.close()
