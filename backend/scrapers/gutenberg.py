"""
Scraper for Project Gutenberg — public domain texts.
Books organized by MCAT CARS topic categories.
"""

import requests
import random
import re
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from quality import is_mcat_suitable

SOURCE_NAME = "Project Gutenberg"

# (gutenberg_id, title, author)
BOOKS_BY_TOPIC = {
    "philosophy": [
        (4280,  "Pragmatism",                          "William James"),
        (1497,  "The Republic",                        "Plato"),
        (1998,  "Thus Spoke Zarathustra",              "Friedrich Nietzsche"),
        (3207,  "Critique of Pure Reason",             "Immanuel Kant"),
        (8438,  "The Varieties of Religious Experience","William James"),
        (2130,  "The Principles of Psychology Vol 1",  "William James"),
        (5827,  "The Problems of Philosophy",          "Bertrand Russell"),
        (14328, "An Enquiry Concerning Human Understanding","David Hume"),
        (4705,  "An Essay Concerning Human Understanding","John Locke"),
        (6763,  "The Phenomenology of Spirit",         "G.W.F. Hegel"),
        (36034, "Beyond Good and Evil",                "Friedrich Nietzsche"),
    ],
    "ethics": [
        (5116,  "Utilitarianism",                      "John Stuart Mill"),
        (34901, "On Liberty",                          "John Stuart Mill"),
        (7370,  "Leviathan",                           "Thomas Hobbes"),
        (9662,  "Unto This Last",                      "John Ruskin"),
        (46,    "A Vindication of the Rights of Woman","Mary Wollstonecraft"),
        (1232,  "The Prince",                          "Niccolò Machiavelli"),
        (61,    "The Subjection of Women",             "John Stuart Mill"),
        (4083,  "The Groundwork of the Metaphysics of Morals","Immanuel Kant"),
    ],
    "social science": [
        (16643, "Democracy and Education",             "John Dewey"),
        (30107, "The Souls of Black Folk",             "W.E.B. Du Bois"),
        (1135,  "The Wealth of Nations",               "Adam Smith"),
        (3296,  "The Interpretation of Dreams",        "Sigmund Freud"),
        (815,   "Democracy in America Vol 1",          "Alexis de Tocqueville"),
        (1283,  "The Theory of the Leisure Class",     "Thorstein Veblen"),
        (362,   "The Condition of the Working Class in England","Friedrich Engels"),
        (16,    "Self-Reliance and Other Essays",      "Ralph Waldo Emerson"),
        (14839, "The Education of Henry Adams",        "Henry Adams"),
    ],
    "natural science": [
        (2852,  "The Descent of Man",                  "Charles Darwin"),
        (33,    "The Origin of Species",               "Charles Darwin"),
        (2940,  "Evolution and Ethics",                "T.H. Huxley"),
        (1572,  "The Grammar of Science",              "Karl Pearson"),
        (38427, "Science and the Modern World",        "Alfred North Whitehead"),
    ],
    "humanities": [
        (16,    "Self-Reliance and Other Essays",      "Ralph Waldo Emerson"),
        (2109,  "Walden",                              "Henry David Thoreau"),
        (8438,  "The Varieties of Religious Experience","William James"),
        (9662,  "Unto This Last",                      "John Ruskin"),
        (30107, "The Souls of Black Folk",             "W.E.B. Du Bois"),
        (46,    "A Vindication of the Rights of Woman","Mary Wollstonecraft"),
        (4267,  "Culture and Anarchy",                 "Matthew Arnold"),
        (14839, "The Education of Henry Adams",        "Henry Adams"),
        (5230,  "The Civilization of the Renaissance in Italy","Jacob Burckhardt"),
        (1228,  "The Soul of Man Under Socialism",     "Oscar Wilde"),
    ],
}

ALL_BOOKS = list({(b[0], b[1], b[2], t) for t, books in BOOKS_BY_TOPIC.items() for b in books})

MAX_WORDS = 530
MIN_WORDS = 380
MAX_ATTEMPTS = 4

SKIP_PREFIXES = (
    "CHAPTER", "SECTION", "BOOK", "PART", "NOTE", "PREFACE",
    "INTRODUCTION", "APPENDIX", "LECTURE", "VOLUME", "_", "[",
    "I.", "II.", "III.", "IV.", "V.", "VI.", "VII.", "VIII.",
    "TRANSLATOR", "EDITOR", "FOOTNOTE",
)


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


def _extract_excerpt(text: str):
    for marker in ["*** START OF", "***START OF"]:
        idx = text.find(marker)
        if idx != -1:
            text = text[idx + len(marker):]
            text = text[text.find("\n") + 1:]
            break
    for marker in ["*** END OF", "***END OF"]:
        idx = text.find(marker)
        if idx != -1:
            text = text[:idx]
            break

    paragraphs = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]
    paragraphs = [
        p for p in paragraphs
        if (len(p.split()) > 30
            and p[0].isupper()
            and not any(p.startswith(s) for s in SKIP_PREFIXES)
            and not re.match(r"^\d", p)
            and "Project Gutenberg" not in p
            and "©" not in p)
    ]

    if len(paragraphs) < 5:
        return None

    max_start = max(1, int(len(paragraphs) * 0.7))
    candidates = random.sample(range(min(max_start, len(paragraphs))), min(MAX_ATTEMPTS, max_start))

    for start in candidates:
        selected = []
        word_count = 0
        for p in paragraphs[start:]:
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


def scrape_random_book(topic: str = None):
    if topic and topic in BOOKS_BY_TOPIC:
        pool = BOOKS_BY_TOPIC[topic]
        book_id, title, author = random.choice(pool)
    else:
        book_id, title, author, _ = random.choice(ALL_BOOKS)

    topic_label = topic or "general"

    for url in (
        f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt",
        f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt",
    ):
        try:
            resp = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
            resp.raise_for_status()
            passage = _extract_excerpt(resp.text)
            if passage:
                return {
                    "source_name": SOURCE_NAME,
                    "source_url": f"https://www.gutenberg.org/ebooks/{book_id}",
                    "source_title": f"{title} — {author}",
                    "topic": topic_label,
                    "passage": passage,
                }
        except requests.RequestException:
            continue

    print(f"Gutenberg fetch failed for {title}")
    return None
