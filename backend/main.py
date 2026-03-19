import os
import sys
import random
import json
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
from generator import generate_questions
from database import init_db, save_passage, get_random_passage, count_passages

app = FastAPI()
init_db()

frontend_path = Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")


@app.get("/")
def index():
    return FileResponse(str(frontend_path / "index.html"))


@app.get("/api/passage")
def get_passage(topic: str = None):
    """Return a random cached passage (filtered by topic if given), otherwise scrape a new one."""
    if count_passages() > 0:
        passage = get_random_passage(topic=topic)
        if passage:
            passage["cached"] = True
            return passage
    return _scrape_and_save(topic=topic)


@app.get("/api/passage/new")
def get_new_passage(topic: str = None):
    """Always scrape a fresh passage."""
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
