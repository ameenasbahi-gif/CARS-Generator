import os
import sys
import random
import json
import time
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

sys.path.insert(0, str(Path(__file__).parent))
from scrapers.sep import scrape_random_entry
from scrapers.gutenberg import scrape_random_book
from generator import generate_questions, ask_followup
from database import init_db, save_passage, get_random_passage, get_passage_by_id, count_passages, flag_question

app = FastAPI()
init_db()

# ── Rate limiter ────────────────────────────────────────────
_last_new_passage_time = 0.0
NEW_PASSAGE_COOLDOWN = 15  # seconds

frontend_path = Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")


@app.get("/")
def index():
    return FileResponse(str(frontend_path / "index.html"))


@app.get("/api/passage")
def get_passage(topic: str = None, id: int = None):
    """Return a passage by id, random cached passage, or scrape a new one."""
    if id is not None:
        passage = get_passage_by_id(id)
        if passage:
            passage["cached"] = True
            return passage
        raise HTTPException(status_code=404, detail="Passage not found.")
    if count_passages() > 0:
        passage = get_random_passage(topic=topic)
        if passage:
            passage["cached"] = True
            return passage
    return _scrape_and_save(topic=topic)


@app.get("/api/passage/new")
def get_new_passage(topic: str = None):
    """Always scrape a fresh passage (rate-limited to 1 per 15s)."""
    global _last_new_passage_time
    elapsed = time.time() - _last_new_passage_time
    if elapsed < NEW_PASSAGE_COOLDOWN:
        raise HTTPException(status_code=429, detail="Please wait before requesting a new passage.")
    _last_new_passage_time = time.time()
    return _scrape_and_save(topic=topic)


FEEDBACK_FILE = Path(__file__).parent.parent / "feedback.jsonl"

class FeedbackPayload(BaseModel):
    message: str

@app.post("/api/feedback")
def submit_feedback(payload: FeedbackPayload):
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="Feedback cannot be empty.")
    entry = {"timestamp": datetime.utcnow().isoformat(), "message": payload.message.strip()}
    with open(FEEDBACK_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return {"ok": True}

@app.get("/api/stats")
def stats():
    return {"passages_cached": count_passages()}


class FlagPayload(BaseModel):
    passage_id: int
    question_index: int

@app.post("/api/flag")
def flag(payload: FlagPayload):
    flag_question(payload.passage_id, payload.question_index)
    return {"status": "flagged"}


class AskPayload(BaseModel):
    passage: str
    question_text: str
    user_answer: str
    correct_answer: str
    explanation: str
    user_question: str

@app.post("/api/ask")
def ask(payload: AskPayload):
    try:
        answer = ask_followup(
            payload.passage,
            payload.question_text,
            payload.user_answer,
            payload.correct_answer,
            payload.explanation,
            payload.user_question,
        )
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ask failed: {e}")


def _scrape_and_save(topic: str = None) -> dict:
    scrapers = [scrape_random_entry, scrape_random_book]
    random.shuffle(scrapers)

    passage_data = None
    for scraper in scrapers:
        passage_data = scraper(topic=topic)
        if passage_data:
            break

    if not passage_data:
        raise HTTPException(status_code=503, detail="Could not scrape a passage. Try again.")

    try:
        questions = generate_questions(passage_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Question generation failed: {e}")

    passage_data["questions"] = questions
    pid = save_passage(passage_data)
    passage_data["id"] = pid
    passage_data["cached"] = False
    return passage_data
