import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "passages.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS passages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_name TEXT,
            source_url TEXT,
            source_title TEXT,
            topic TEXT,
            passage TEXT,
            questions TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def save_passage(data: dict) -> int:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute(
        """INSERT INTO passages (source_name, source_url, source_title, topic, passage, questions)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (
            data.get("source_name", ""),
            data.get("source_url", ""),
            data.get("source_title", ""),
            data.get("topic", ""),
            data.get("passage", ""),
            json.dumps(data.get("questions", [])),
        ),
    )
    pid = cursor.lastrowid
    conn.commit()
    conn.close()
    return pid


def get_random_passage(topic: str = None):
    conn = sqlite3.connect(DB_PATH)
    if topic:
        row = conn.execute(
            "SELECT id, source_name, source_url, source_title, topic, passage, questions FROM passages WHERE topic LIKE ? ORDER BY RANDOM() LIMIT 1",
            (f"%{topic}%",)
        ).fetchone()
    else:
        row = conn.execute(
            "SELECT id, source_name, source_url, source_title, topic, passage, questions FROM passages ORDER BY RANDOM() LIMIT 1"
        ).fetchone()
    conn.close()
    if not row:
        return None
    return {
        "id": row[0],
        "source_name": row[1],
        "source_url": row[2],
        "source_title": row[3],
        "topic": row[4],
        "passage": row[5],
        "questions": json.loads(row[6]),
    }


def count_passages() -> int:
    conn = sqlite3.connect(DB_PATH)
    count = conn.execute("SELECT COUNT(*) FROM passages").fetchone()[0]
    conn.close()
    return count
