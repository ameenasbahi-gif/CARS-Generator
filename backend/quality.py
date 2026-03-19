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
    "by contrast", "on the other hand", "it is worth noting",
    "insofar as", "inasmuch as", "to the extent that",
    "problematic", "undermine", "challenge", "tension between",
]

# Abstract academic vocabulary rewarded by MCAT CARS
ACADEMIC_VOCAB = [
    "epistemological", "ontological", "phenomenological", "empirical",
    "normative", "prescriptive", "descriptive", "conceptual", "theoretical",
    "dialectical", "hermeneutic", "ideological", "institutional", "structural",
    "determinism", "reductionism", "relativism", "objectivity", "subjectivity",
    "rationality", "morality", "consciousness", "perception", "cognition",
    "causality", "contingent", "necessary", "universal", "particular",
    "paradigm", "framework", "discourse", "critique", "analysis",
]

# Signals this is NOT a good CARS passage
DISQUALIFIERS = [
    r'^\s*[A-Z][A-Z\s]{5,}$',     # ALL CAPS headings
    r'^\s*\d+\.',                   # Numbered lists
    r'^\s*[-•]',                    # Bullet points
    r'\[[\d,\s]+\]',               # Citation brackets like [1, 2]
    r'Chapter \d+',                 # Chapter headers in text
    r'www\.|http',                  # URLs
    r'^\s*\([ivxlIVXL]+\)',        # Roman numeral lists
    r'Table \d+|Figure \d+',       # Tables/figures (not CARS)
]


def score_passage(text: str) -> float:
    """
    Return a quality score 0.0-1.0 for MCAT CARS suitability.
    Passages scoring >= 0.55 are accepted.
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
    score += min(arg_hits / 7, 1.0) * 0.35

    # 2. Sentence complexity — avg words per sentence (0-0.20)
    if sentences:
        avg_sentence_len = word_count / len(sentences)
        if avg_sentence_len >= 20:
            score += 0.20
        elif avg_sentence_len >= 17:
            score += 0.13
        elif avg_sentence_len >= 14:
            score += 0.06

    # 3. Lexical diversity — ratio of unique words (0-0.12)
    unique_ratio = len(set(w.lower() for w in words)) / max(word_count, 1)
    score += min(unique_ratio * 0.4, 0.12)

    # 4. No excessive dialogue (0-0.12)
    dialogue_count = text.count('"') + text.count('\u201c') + text.count('\u201d')
    if dialogue_count < 4:
        score += 0.12
    elif dialogue_count < 8:
        score += 0.05

    # 5. Paragraph structure — at least 2 paragraphs (0-0.08)
    paragraphs = [p for p in text.split('\n\n') if len(p.split()) > 20]
    if len(paragraphs) >= 3:
        score += 0.08
    elif len(paragraphs) >= 2:
        score += 0.04

    # 6. Hard disqualifiers — subtract heavily
    for pattern in DISQUALIFIERS:
        if re.search(pattern, text, re.MULTILINE):
            score -= 0.25

    # 7. Nuance / hedging language (0-0.06)
    nuance_words = ["although", "while", "despite", "yet", "however",
                    "complex", "tension", "ambiguous", "nuanced", "paradox",
                    "not merely", "not simply", "more than", "rather than"]
    nuance_hits = sum(1 for w in nuance_words if w in text_lower)
    score += min(nuance_hits * 0.015, 0.06)

    # 8. Academic vocabulary bonus (0-0.07)
    vocab_hits = sum(1 for w in ACADEMIC_VOCAB if w in text_lower)
    score += min(vocab_hits * 0.02, 0.07)

    # 9. Penalty: too many proper nouns = biographical/narrative (up to -0.20)
    cap_words = re.findall(r'(?<![.!?]\s)(?<!\n)\b[A-Z][a-z]{2,}\b', text)
    proper_noun_ratio = len(cap_words) / max(word_count, 1)
    if proper_noun_ratio > 0.08:
        score -= 0.20
    elif proper_noun_ratio > 0.05:
        score -= 0.10

    # 10. Penalty: past-tense narrative writing (not analytical)
    past_tense = len(re.findall(
        r'\b(was|were|had|said|went|came|took|gave|saw|knew|thought|felt|became)\b',
        text_lower
    ))
    past_ratio = past_tense / max(word_count, 1)
    if past_ratio > 0.04:
        score -= 0.15
    elif past_ratio > 0.025:
        score -= 0.07

    return max(0.0, min(score, 1.0))


def is_mcat_suitable(text: str, threshold: float = 0.55) -> bool:
    return score_passage(text) >= threshold
