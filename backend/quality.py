"""
Rule-based passage quality filter for MCAT CARS suitability.
Scores passages without API calls — fast and free.

MCAT CARS passages are:
- Argumentative / analytical (not purely descriptive or narrative)
- Dense academic prose with complex sentence structure
- 500-600 words, coherent standalone excerpt
- Humanities, social science, or natural science for general audiences
- NOT: biographical timelines, dialogue-heavy, lists, poetry
"""

import re

# Words that signal argumentation and analysis — core to MCAT CARS
ARGUMENT_SIGNALS = [
    "argues", "argue", "contends", "contend", "suggests", "suggest",
    "claims", "claim", "asserts", "assert", "maintains", "maintain",
    "however", "nevertheless", "nonetheless", "although", "whereas",
    "therefore", "thus", "hence", "consequently", "accordingly",
    "moreover", "furthermore", "in contrast", "on the contrary",
    "paradoxically", "ironically", "significantly", "notably",
    "it follows", "one must", "we must", "one might", "implies",
    "underlying", "fundamental", "inherently", "essentially",
    "presupposes", "assumption", "conception", "notion", "distinction",
]

# Signals this is NOT a good CARS passage
DISQUALIFIERS = [
    r'^\s*[A-Z][A-Z\s]{5,}$',     # ALL CAPS headings
    r'^\s*\d+\.',                   # Numbered lists
    r'^\s*[-•]',                    # Bullet points
    r'\[[\d,\s]+\]',               # Citation brackets like [1, 2]
    r'Chapter \d+',                 # Chapter headers in text
    r'www\.|http',                  # URLs
]


def score_passage(text: str) -> float:
    """
    Return a quality score 0.0-1.0 for MCAT CARS suitability.
    Passages scoring >= 0.45 are accepted.
    """
    if not text or len(text.split()) < 300:
        return 0.0

    score = 0.0
    text_lower = text.lower()
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if len(s.split()) > 3]
    words = text.split()
    word_count = len(words)

    # 1. Argument density (0-0.35)
    arg_hits = sum(1 for signal in ARGUMENT_SIGNALS if signal in text_lower)
    score += min(arg_hits / 6, 1.0) * 0.35

    # 2. Sentence complexity — avg words per sentence (0-0.20)
    if sentences:
        avg_sentence_len = word_count / len(sentences)
        # MCAT passages typically have avg sentence length 18-28 words
        if avg_sentence_len >= 18:
            score += 0.20
        elif avg_sentence_len >= 14:
            score += 0.10

    # 3. Lexical diversity — ratio of unique words (0-0.15)
    unique_ratio = len(set(w.lower() for w in words)) / max(word_count, 1)
    score += min(unique_ratio * 0.5, 0.15)

    # 4. No excessive dialogue (0-0.15)
    dialogue_count = text.count('"') + text.count('"') + text.count('"')
    if dialogue_count < 4:
        score += 0.15
    elif dialogue_count < 8:
        score += 0.07

    # 5. Paragraph structure — at least 2 paragraphs (0-0.10)
    paragraphs = [p for p in text.split('\n\n') if len(p.split()) > 20]
    if len(paragraphs) >= 3:
        score += 0.10
    elif len(paragraphs) >= 2:
        score += 0.05

    # 6. Hard disqualifiers — subtract heavily
    for pattern in DISQUALIFIERS:
        if re.search(pattern, text, re.MULTILINE):
            score -= 0.25

    # 7. Bonus: contains hedging/nuance language typical of academic writing
    nuance_words = ["although", "while", "despite", "yet", "but", "however",
                    "complex", "tension", "ambiguous", "nuanced", "paradox"]
    nuance_hits = sum(1 for w in nuance_words if w in text_lower)
    score += min(nuance_hits * 0.02, 0.05)

    return max(0.0, min(score, 1.0))


def is_mcat_suitable(text: str, threshold: float = 0.45) -> bool:
    return score_passage(text) >= threshold
