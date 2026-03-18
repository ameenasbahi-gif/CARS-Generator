"""
Jack Westin CARS Passage Scraper
---------------------------------
Uses Playwright (headless Chromium) because Jack Westin is a React app
that blocks plain HTTP requests.

Passage list:  https://jackwestin.com/daily/mcat-practice-passages/cars-practice-passages/
Each passage:  https://jackwestin.com/resources/cars-passage/<slug>

Rate limit:    1 request / 3 seconds  (respectful crawling)
"""

import asyncio
import re
import logging
from typing import Optional
from playwright.async_api import async_playwright, Page, TimeoutError as PWTimeout

from database import upsert_passage

log = logging.getLogger("jack_westin")

BASE_URL = "https://jackwestin.com"
LIST_URL = f"{BASE_URL}/daily/mcat-practice-passages/cars-practice-passages/"
RATE_LIMIT_SECS = 3
MAX_PASSAGES = 60  # Scrape up to 60 passages per run


# ── Category mapping ────────────────────────────────────────────────────────

_HUMANITIES_KEYWORDS = {
    "art", "music", "literature", "poetry", "philosophy", "aesthetics",
    "ethics", "theater", "dance", "architecture", "religion", "film",
    "language", "linguistics", "culture", "history", "mythology",
}
_SOCIAL_KEYWORDS = {
    "economics", "sociology", "anthropology", "political", "psychology",
    "education", "geography", "archaeology", "population", "governance",
    "democracy", "social", "gender", "race", "identity", "media",
}


def classify_category(title: str, text: str) -> tuple[str, str]:
    """Heuristically assign MCAT CARS category from title + first paragraph."""
    combined = (title + " " + text[:400]).lower()
    h_score = sum(1 for kw in _HUMANITIES_KEYWORDS if kw in combined)
    s_score = sum(1 for kw in _SOCIAL_KEYWORDS if kw in combined)
    if h_score >= s_score:
        return "humanities", "Humanities"
    elif s_score > h_score:
        return "social", "Social Sciences"
    else:
        return "natural", "Natural Sciences"


# ── Parsing helpers ─────────────────────────────────────────────────────────

def clean_text(text: str) -> str:
    """Collapse whitespace and strip junk characters."""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def parse_question_block(block_text: str) -> Optional[dict]:
    """
    Parse a raw question block into structured data.

    Expected format (Jack Westin):
        <question stem>
        A. Option text
        B. Option text
        C. Option text
        D. Option text
        [Correct answer + explanation may follow]
    """
    lines = [l.strip() for l in block_text.splitlines() if l.strip()]
    if len(lines) < 5:
        return None

    options = []
    option_pattern = re.compile(r"^([A-D])[.)]\s+(.+)$")
    stem_lines = []
    correct_idx = None
    explanation_lines = []
    in_options = False
    in_explanation = False

    for line in lines:
        m = option_pattern.match(line)
        if m:
            in_options = True
            options.append(m.group(2))
        elif in_options and re.match(r"^(correct|answer)[:\s]", line, re.I):
            # "Correct answer: B" or "Answer: C"
            letter = re.search(r"[A-D]", line)
            if letter:
                correct_idx = ord(letter.group()) - ord("A")
            in_explanation = True
        elif in_explanation:
            explanation_lines.append(line)
        elif not in_options:
            stem_lines.append(line)

    if len(options) != 4 or not stem_lines:
        return None

    return {
        "text": clean_text(" ".join(stem_lines)),
        "options": [clean_text(o) for o in options],
        "correct": correct_idx if correct_idx is not None else 0,
        "explanation": clean_text(" ".join(explanation_lines)),
    }


# ── Main scraper ────────────────────────────────────────────────────────────

class JackWestinScraper:

    async def scrape(self) -> int:
        """Scrape Jack Westin CARS passages. Returns number of passages saved."""
        saved = 0
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/122.0.0.0 Safari/537.36"
                ),
                viewport={"width": 1280, "height": 900},
            )
            page = await context.new_page()

            try:
                links = await self._get_passage_links(page)
                log.info(f"Jack Westin: found {len(links)} passage links")

                for url in links[:MAX_PASSAGES]:
                    try:
                        result = await self._scrape_passage(page, url)
                        if result:
                            saved += 1
                            log.info(f"Saved: {result['title']}")
                        await asyncio.sleep(RATE_LIMIT_SECS)
                    except Exception as e:
                        log.warning(f"Failed passage {url}: {e}")
                        continue

            finally:
                await browser.close()

        log.info(f"Jack Westin scrape complete. Saved {saved} passages.")
        return saved

    async def _get_passage_links(self, page: Page) -> list[str]:
        """Return list of individual passage URLs from the listing page."""
        try:
            await page.goto(LIST_URL, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(2000)
        except PWTimeout:
            log.warning("List page load timed out — proceeding with partial DOM")

        # Jack Westin passage cards: look for links inside passage-list items
        # Selectors may need adjustment if site structure changes
        links = await page.eval_on_selector_all(
            "a[href*='cars-passage'], a[href*='cars_passage'], "
            "a[href*='/resources/'][href*='passage']",
            "els => els.map(e => e.href)"
        )

        # De-duplicate while preserving order
        seen = set()
        unique = []
        for url in links:
            if url not in seen and BASE_URL in url:
                seen.add(url)
                unique.append(url)
        return unique

    async def _scrape_passage(self, page: Page, url: str) -> Optional[dict]:
        """Scrape a single passage page and persist it."""
        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(1500)
        except PWTimeout:
            pass  # Proceed with whatever loaded

        # ── Title ──
        title = await self._try_selectors(page, [
            "h1.passage-title", "h1", ".entry-title",
            "[class*='title']", "h2",
        ])
        if not title:
            return None

        # ── Passage text ──
        # Jack Westin wraps passage text in a specific container
        text = await self._try_selectors(page, [
            ".passage-text", ".cars-passage-content",
            "[class*='passage'][class*='content']",
            ".passage-body", "article .content",
            ".entry-content > p",          # WordPress fallback
        ])
        if not text or len(text) < 200:
            return None

        # ── Questions ──
        # Questions are rendered as individual blocks after the passage
        question_els = await page.query_selector_all(
            ".question-block, [class*='question-item'], "
            "[class*='question-container'], .cars-question"
        )

        questions = []
        if question_els:
            for el in question_els:
                raw = await el.inner_text()
                q = parse_question_block(raw)
                if q:
                    questions.append(q)

        # Skip if fewer than 4 questions (probably didn't parse correctly)
        if len(questions) < 4:
            log.warning(f"Only {len(questions)} questions parsed for {url} — skipping")
            return None

        category, category_label = classify_category(title, text)

        passage_id = upsert_passage(
            title=clean_text(title),
            text=f"<p>{clean_text(text).replace(chr(10), '</p><p>')}</p>",
            category=category,
            source=f"Jack Westin — {category_label}",
            source_url=url,
            questions=questions,
        )

        return {"id": passage_id, "title": title}

    async def _try_selectors(self, page: Page, selectors: list[str]) -> Optional[str]:
        """Try a list of CSS selectors in order, return inner text of first match."""
        for sel in selectors:
            try:
                el = await page.query_selector(sel)
                if el:
                    text = await el.inner_text()
                    if text and len(text.strip()) > 30:
                        return text.strip()
            except Exception:
                continue
        return None
