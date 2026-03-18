"""
Khan Academy MCAT CARS Scraper
---------------------------------
Khan Academy exposes content via an internal REST API.
MCAT CARS passages live under the 'mcat' topic tree.

API root:   https://www.khanacademy.org/api/v1/topic/mcat
CARS slug:  mcat-cars  (Critical Analysis and Reasoning Skills)

Each exercise node contains:
  - A reading passage (the "context" field in perseus content)
  - Multiple choice questions

Rate limit: 1 request / 2 seconds
"""

import asyncio
import json
import logging
import re
from typing import Optional

import httpx

from database import upsert_passage

log = logging.getLogger("khan_academy")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/html, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.khanacademy.org/",
}

# KA API endpoints
TOPIC_API = "https://www.khanacademy.org/api/v1/topic/{slug}"
EXERCISE_API = "https://www.khanacademy.org/api/v1/exercises/{slug}"

# MCAT CARS topic slugs to crawl
CARS_TOPIC_SLUGS = [
    "mcat-cars",
    "critical-analysis-and-reasoning-skills",
    "cars-passage-1",
    "cars-passages",
]

RATE_LIMIT_SECS = 2
MAX_PASSAGES = 35  # KA has ~35 CARS passages


# ── Perseus content parser ──────────────────────────────────────────────────

def strip_perseus_markdown(text: str) -> str:
    """Remove Perseus/KaTeX markup and clean plain text."""
    # Remove math blocks: $...$  or  \\(...\\)
    text = re.sub(r"\$\$.*?\$\$", "", text, flags=re.DOTALL)
    text = re.sub(r"\$.*?\$", "", text)
    text = re.sub(r"\\\(.*?\\\)", "", text, flags=re.DOTALL)
    # Remove widget references: [[☃ passage 1]]
    text = re.sub(r"\[\[.*?\]\]", "", text)
    # Remove bold/italic markers
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    # Collapse whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def perseus_to_html(text: str) -> str:
    """Convert Perseus markdown paragraphs to HTML <p> tags."""
    text = strip_perseus_markdown(text)
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    return "".join(f"<p>{p}</p>" for p in paragraphs)


def parse_perseus_item(item_data: dict) -> Optional[dict]:
    """
    Parse a Perseus exercise item into {text, options, correct, explanation}.
    """
    try:
        question = item_data.get("question", {})
        content = question.get("content", "")
        widgets = question.get("widgets", {})

        # Find the radio widget (multiple choice)
        radio_widget = None
        for key, widget in widgets.items():
            if widget.get("type") == "radio":
                radio_widget = widget
                break

        if not radio_widget:
            return None

        choices = radio_widget.get("options", {}).get("choices", [])
        if len(choices) < 2:
            return None

        options = [strip_perseus_markdown(c.get("content", "")) for c in choices]
        correct_indices = [i for i, c in enumerate(choices) if c.get("correct")]
        if not correct_indices:
            return None
        correct = correct_indices[0]

        # Explanation from rationale
        rationale = radio_widget.get("options", {}).get("rationale", "")
        if not rationale:
            rationale = choices[correct].get("rationale", "")
        explanation = strip_perseus_markdown(rationale)

        stem = strip_perseus_markdown(content)
        if not stem:
            return None

        return {
            "text": stem,
            "options": options,
            "correct": correct,
            "explanation": explanation,
        }
    except Exception as e:
        log.warning(f"Failed to parse Perseus item: {e}")
        return None


def extract_passage_from_exercise(exercise_data: dict) -> Optional[str]:
    """
    Extract the reading passage from a KA exercise.
    Passages live in 'passage' type widgets in the exercise's items.
    """
    items = exercise_data.get("items", []) or exercise_data.get("questions", [])
    for item in items:
        q = item.get("item_data", item)
        if isinstance(q, str):
            try:
                q = json.loads(q)
            except Exception:
                continue
        question = q.get("question", {})
        widgets = question.get("widgets", {})
        for key, widget in widgets.items():
            if widget.get("type") == "passage":
                raw = widget.get("options", {}).get("passageText", "")
                if raw and len(raw) > 200:
                    return raw
    return None


# ── Main scraper ────────────────────────────────────────────────────────────

class KhanAcademyScraper:

    def __init__(self):
        self.client = httpx.AsyncClient(
            headers=HEADERS,
            follow_redirects=True,
            timeout=20.0,
        )

    async def scrape(self) -> int:
        """Scrape Khan Academy MCAT CARS exercises. Returns passages saved."""
        saved = 0
        try:
            exercise_slugs = await self._discover_exercises()
            log.info(f"Khan Academy: found {len(exercise_slugs)} CARS exercises")

            for slug in exercise_slugs[:MAX_PASSAGES]:
                try:
                    result = await self._scrape_exercise(slug)
                    if result:
                        saved += 1
                        log.info(f"Saved KA passage: {result['title']}")
                    await asyncio.sleep(RATE_LIMIT_SECS)
                except Exception as e:
                    log.warning(f"Failed KA exercise {slug}: {e}")
                    continue
        finally:
            await self.client.aclose()

        log.info(f"Khan Academy scrape complete. Saved {saved} passages.")
        return saved

    async def _discover_exercises(self) -> list[str]:
        """Walk the KA topic tree to find CARS exercise slugs."""
        exercise_slugs = []

        for topic_slug in CARS_TOPIC_SLUGS:
            try:
                url = TOPIC_API.format(slug=topic_slug)
                resp = await self.client.get(url)
                if resp.status_code != 200:
                    continue

                data = resp.json()
                # Recursively collect exercise slugs from children
                self._collect_exercises(data, exercise_slugs)
                await asyncio.sleep(RATE_LIMIT_SECS)

            except Exception as e:
                log.warning(f"Topic {topic_slug} failed: {e}")
                continue

        # De-duplicate
        return list(dict.fromkeys(exercise_slugs))

    def _collect_exercises(self, node: dict, result: list):
        """Recursively collect exercise slugs from a topic tree node."""
        kind = node.get("kind", "")
        if kind == "Exercise":
            slug = node.get("slug") or node.get("node_slug")
            if slug:
                result.append(slug)
            return

        children = (
            node.get("children", []) or
            node.get("child_data", []) or
            node.get("topic_page", {}).get("subtopics", [])
        )
        for child in children:
            self._collect_exercises(child, result)

    async def _scrape_exercise(self, slug: str) -> Optional[dict]:
        """Scrape a single KA exercise by slug."""
        try:
            url = EXERCISE_API.format(slug=slug)
            resp = await self.client.get(url)
            if resp.status_code != 200:
                return None
            data = resp.json()
        except Exception as e:
            log.warning(f"Exercise fetch failed {slug}: {e}")
            return None

        title = data.get("display_name") or data.get("title") or slug.replace("-", " ").title()

        # Extract passage text
        passage_raw = extract_passage_from_exercise(data)
        if not passage_raw or len(passage_raw) < 200:
            return None
        passage_html = perseus_to_html(passage_raw)

        # Extract questions
        items = data.get("items", []) or data.get("questions", [])
        questions = []
        for item in items:
            raw_item = item.get("item_data", item)
            if isinstance(raw_item, str):
                try:
                    raw_item = json.loads(raw_item)
                except Exception:
                    continue
            q = parse_perseus_item(raw_item)
            if q:
                questions.append(q)

        if len(questions) < 3:
            log.warning(f"Too few questions ({len(questions)}) for KA {slug}")
            return None

        # Determine category
        tags = [t.lower() for t in (data.get("tags") or data.get("exercise_tags") or [])]
        if any(t in tags for t in ["humanities", "art", "philosophy", "literature"]):
            category, category_label = "humanities", "Humanities"
        elif any(t in tags for t in ["social", "sociology", "economics", "political"]):
            category, category_label = "social", "Social Sciences"
        else:
            category, category_label = "humanities", "Humanities"  # KA CARS default

        source_url = f"https://www.khanacademy.org/test-prep/mcat/cars/{slug}/e/{slug}"

        passage_id = upsert_passage(
            title=title,
            text=passage_html,
            category=category,
            source=f"Khan Academy MCAT — {category_label}",
            source_url=source_url,
            questions=questions,
        )

        return {"id": passage_id, "title": title}
