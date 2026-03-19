"""
Scraper for Stanford Encyclopedia of Philosophy (plato.stanford.edu).
All content is open access. Entries organized by MCAT CARS topic categories.
"""

import requests
import random
import sys
import os
from bs4 import BeautifulSoup
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from quality import is_mcat_suitable

BASE_URL = "https://plato.stanford.edu"
SOURCE_NAME = "Stanford Encyclopedia of Philosophy"
MAX_ATTEMPTS = 3
MAX_WORDS = 530
MIN_WORDS = 380

ENTRIES_BY_TOPIC = {
    "philosophy": [
        "consciousness", "qualia", "mind-body", "personal-identity",
        "free-will", "meaning", "language-thought", "truth",
        "causation-metaphysics", "perception", "memory", "emotion",
        "knowledge-analysis", "naturalism", "reductionism",
    ],
    "ethics": [
        "consequentialism", "deontological-ethics", "virtue-ethics",
        "moral-realism", "well-being", "justice", "equality",
        "autonomy-moral", "social-contract", "feminism-ethics",
    ],
    "social science": [
        "democracy", "race", "disability", "identity-personal",
        "scientific-explanation", "science-theory-observation",
    ],
    "natural science": [
        "science-theory-observation", "scientific-explanation",
        "naturalism", "reductionism", "causation-metaphysics",
        "emergence",
    ],
    "humanities": [
        "beauty", "art-definition", "death", "memory", "emotion",
        "perception", "language-thought", "meaning",
    ],
}

# Flat list for when no topic filter is applied
ALL_ENTRIES = list({slug for slugs in ENTRIES_BY_TOPIC.values() for slug in slugs})


def _truncate_to_sentence(text: str, max_words: int) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    truncated = " ".join(words[:max_words])
    for punct in (".", "!", "?"):
        idx = truncated.rfind(punct)
        if idx > len(truncated) // 2:
            return truncated[:idx + 1]
    return truncated


def _extract_passage(soup: BeautifulSoup):
    article = soup.find("div", id="main-text") or soup.find("div", {"id": "article"})
    if not article:
        return None

    all_paragraphs = []
    for tag in article.find_all("p", recursive=True):
        if tag.find_parent(class_=["notes", "bibliography", "toc", "see-also"]):
            continue
        text = tag.get_text(" ", strip=True)
        words = text.split()
        if len(words) < 25 or not text[0].isupper():
            continue
        if text.count("[") > 3:
            continue
        all_paragraphs.append(text)

    if len(all_paragraphs) < 5:
        return None

    max_start = max(1, int(len(all_paragraphs) * 0.7))
    candidates = random.sample(range(max_start), min(MAX_ATTEMPTS, max_start))

    for start in candidates:
        selected = []
        word_count = 0
        for p in all_paragraphs[start:]:
            selected.append(p)
            word_count += len(p.split())
            if word_count >= MAX_WORDS:
                break
        if word_count < MIN_WORDS:
            continue
        passage = _truncate_to_sentence("\n\n".join(selected), MAX_WORDS)
        if is_mcat_suitable(passage):
            return passage

    return None


def scrape_random_entry(topic: str = None):
    pool = ENTRIES_BY_TOPIC.get(topic, ALL_ENTRIES) if topic else ALL_ENTRIES
    slug = random.choice(pool)
    url = f"{BASE_URL}/entries/{slug}/"

    try:
        resp = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"SEP fetch failed for {slug}: {e}")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")
    title_tag = soup.find("h1") or soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else slug.replace("-", " ").title()

    passage = _extract_passage(soup)
    if not passage:
        return None

    return {
        "source_name": SOURCE_NAME,
        "source_url": url,
        "source_title": title,
        "topic": slug.replace("-", " "),
        "passage": passage,
    }
