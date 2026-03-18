from pydantic import BaseModel
from typing import List, Optional


class Question(BaseModel):
    id: int
    text: str
    options: List[str]
    correct: int
    explanation: str


class Passage(BaseModel):
    id: int
    title: str
    text: str
    category: str           # "humanities" | "social" | "natural"
    category_label: str
    source: str
    source_url: Optional[str] = None
    questions: List[Question]


class PassageSummary(BaseModel):
    id: int
    title: str
    category: str
    category_label: str
    source: str
    question_count: int


class ScrapeStatus(BaseModel):
    jack_westin: str
    khan_academy: str
    total_passages: int
