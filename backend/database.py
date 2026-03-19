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
    # Add flagged_questions column to existing DBs if missing
    try:
        conn.execute("ALTER TABLE passages ADD COLUMN flagged_questions TEXT DEFAULT '[]'")
        conn.commit()
    except Exception:
        pass  # Column already exists

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            settings TEXT DEFAULT '{}'
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            passages_completed INTEGER DEFAULT 0,
            questions_correct INTEGER DEFAULT 0,
            questions_total INTEGER DEFAULT 0,
            topic TEXT,
            question_type_stats TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()


# ── User auth ───────────────────────────────────────────────

def create_user(username: str, password_hash: str):
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash)
        )
        uid = cursor.lastrowid
        conn.commit()
        row = conn.execute("SELECT id, username, settings FROM users WHERE id = ?", (uid,)).fetchone()
        conn.close()
        return {"id": row[0], "username": row[1], "settings": json.loads(row[2] or "{}")}
    except Exception:
        conn.close()
        return None


def get_user_by_username(username: str):
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        "SELECT id, username, password_hash, settings FROM users WHERE username = ?", (username,)
    ).fetchone()
    conn.close()
    if not row:
        return None
    return {"id": row[0], "username": row[1], "password_hash": row[2], "settings": json.loads(row[3] or "{}")}


def get_user_by_id(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        "SELECT id, username, password_hash, settings FROM users WHERE id = ?", (user_id,)
    ).fetchone()
    conn.close()
    if not row:
        return None
    return {"id": row[0], "username": row[1], "password_hash": row[2], "settings": json.loads(row[3] or "{}")}


def update_user_settings(user_id: int, settings: dict):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE users SET settings = ? WHERE id = ?", (json.dumps(settings), user_id))
    conn.commit()
    conn.close()


# ── User progress ───────────────────────────────────────────

def save_user_progress(user_id: int, date: str, passages_completed: int,
                       questions_correct: int, questions_total: int,
                       topic: str, question_type_stats: dict):
    conn = sqlite3.connect(DB_PATH)
    existing = conn.execute(
        "SELECT id FROM user_progress WHERE user_id = ? AND date = ?", (user_id, date)
    ).fetchone()
    if existing:
        conn.execute("""
            UPDATE user_progress
            SET passages_completed = passages_completed + ?,
                questions_correct = questions_correct + ?,
                questions_total = questions_total + ?,
                topic = ?,
                question_type_stats = ?
            WHERE user_id = ? AND date = ?
        """, (passages_completed, questions_correct, questions_total,
              topic, json.dumps(question_type_stats), user_id, date))
    else:
        conn.execute("""
            INSERT INTO user_progress
            (user_id, date, passages_completed, questions_correct, questions_total, topic, question_type_stats)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, date, passages_completed, questions_correct, questions_total,
              topic, json.dumps(question_type_stats)))
    conn.commit()
    conn.close()


def get_user_stats(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT date, passages_completed, questions_correct, questions_total, topic, question_type_stats "
        "FROM user_progress WHERE user_id = ? ORDER BY date DESC",
        (user_id,)
    ).fetchall()
    conn.close()

    total_passages = sum(r[1] for r in rows)
    total_correct = sum(r[2] for r in rows)
    total_questions = sum(r[3] for r in rows)

    # Best topic (highest accuracy, min 3 passages)
    topic_stats = {}
    for r in rows:
        t = r[4] or "general"
        if t not in topic_stats:
            topic_stats[t] = {"correct": 0, "total": 0, "passages": 0}
        topic_stats[t]["correct"] += r[2]
        topic_stats[t]["total"] += r[3]
        topic_stats[t]["passages"] += r[1]
    best_topic = None
    best_ratio = -1
    for t, s in topic_stats.items():
        if s["passages"] >= 3 and s["total"] > 0:
            ratio = s["correct"] / s["total"]
            if ratio > best_ratio:
                best_ratio = ratio
                best_topic = t

    # Weakest question type (lowest accuracy, min 3 attempts)
    type_stats = {}
    for r in rows:
        try:
            qts = json.loads(r[5] or "{}")
        except Exception:
            qts = {}
        for qt, s in qts.items():
            if qt not in type_stats:
                type_stats[qt] = {"correct": 0, "total": 0}
            type_stats[qt]["correct"] += s.get("correct", 0)
            type_stats[qt]["total"] += s.get("total", 0)
    weakest_type = None
    weakest_ratio = 2.0
    for qt, s in type_stats.items():
        if s["total"] >= 3:
            ratio = s["correct"] / s["total"]
            if ratio < weakest_ratio:
                weakest_ratio = ratio
                weakest_type = {"type": qt, "correct": s["correct"], "total": s["total"]}

    # Current streak (consecutive days with passages_completed > 0, from today backwards)
    all_active_dates = sorted(
        {r[0] for r in rows if r[1] > 0}, reverse=True
    )
    current_streak = 0
    if all_active_dates:
        from datetime import date as date_cls, timedelta
        check = date_cls.today()
        for d in all_active_dates:
            try:
                day = date_cls.fromisoformat(d)
            except Exception:
                break
            if day == check or day == check - timedelta(days=1):
                current_streak += 1
                check = day - timedelta(days=1)
            else:
                break

    # All-time streak (max consecutive days)
    all_time_streak = 0
    if all_active_dates:
        from datetime import date as date_cls, timedelta
        sorted_dates = sorted(all_active_dates)
        streak = 1
        max_streak = 1
        for i in range(1, len(sorted_dates)):
            try:
                d1 = date_cls.fromisoformat(sorted_dates[i - 1])
                d2 = date_cls.fromisoformat(sorted_dates[i])
                if d2 - d1 == timedelta(days=1):
                    streak += 1
                    max_streak = max(max_streak, streak)
                else:
                    streak = 1
            except Exception:
                streak = 1
        all_time_streak = max_streak

    # Recent 7 days
    recent = [
        {"date": r[0], "passages": r[1], "correct": r[2], "total": r[3], "topic": r[4]}
        for r in rows[:7]
    ]

    return {
        "total_passages": total_passages,
        "total_correct": total_correct,
        "total_questions": total_questions,
        "best_topic": best_topic,
        "weakest_type": weakest_type,
        "current_streak": current_streak,
        "all_time_streak": all_time_streak,
        "recent": recent,
    }


def flag_question(passage_id: int, question_index: int):
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        "SELECT flagged_questions FROM passages WHERE id = ?", (passage_id,)
    ).fetchone()
    if not row:
        conn.close()
        return
    flagged = json.loads(row[0] or "[]")
    if question_index not in flagged:
        flagged.append(question_index)
    conn.execute(
        "UPDATE passages SET flagged_questions = ? WHERE id = ?",
        (json.dumps(flagged), passage_id)
    )
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


def get_passage_by_id(passage_id: int):
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        "SELECT id, source_name, source_url, source_title, topic, passage, questions FROM passages WHERE id = ?",
        (passage_id,)
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
