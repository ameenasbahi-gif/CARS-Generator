"""
Uses Claude to generate MCAT CARS-style questions and explanations
for a scraped passage.
"""

import anthropic
import json

client = anthropic.Anthropic()

PROMPT = """You are writing questions for a real MCAT CARS practice tool. Generate exactly 5 questions for the passage below. These must be indistinguishable in quality and style from official AAMC CARS questions.

PASSAGE:
{passage}

SOURCE: {source_title} ({source_name})

━━━ QUESTION TYPE REQUIREMENTS ━━━

Write exactly one question of each type, in this order:

1. PRIMARY PURPOSE — Use stem: "The central argument of the passage is..." or "The author's primary purpose in this passage is to..."
   - Correct answer captures the FULL scope (not too narrow, not too broad)
   - Wrong answers: one too narrow (just one paragraph's point), one too broad (overstates), one that misidentifies the author's stance

2. AUTHOR'S ATTITUDE — Use stem: "The author's attitude toward [X] is best described as..." or "The author's tone in discussing [X] can be characterized as..."
   - Pick an attitude word that is precise: not just "critical" but "cautiously skeptical" or "guardedly optimistic"
   - Wrong answers: one that is too extreme, one that is the opposite valence, one that is neutral when the author is not

3. INFERENCE — Use stem: "Which of the following is most strongly supported by the passage?" or "The passage implies that..."
   - Correct answer must be a logical conclusion — not stated directly, but clearly supported
   - Wrong answers: one that is plausible but goes beyond what the text supports, one that contradicts the passage, one that is true but from a different part of the argument

4. SPECIFIC DETAIL — Use stem: "According to the passage..." or "The author states that..."
   - Correct answer must be directly verifiable in the text — quote a paraphrase of an actual sentence
   - Wrong answers: one that inverts a detail, one that confuses two concepts mentioned in the passage, one that is never mentioned

5. APPLICATION — Use stem: "The author would most likely respond to the following claim by..." or "Which of the following scenarios is most analogous to [concept from passage]?"
   - Correct answer applies the author's actual argument or logic to a new situation
   - Wrong answers: one that applies a different author's view, one that contradicts the author's position, one that is irrelevant

━━━ UNIVERSAL RULES (apply to all 5 questions) ━━━

DISTRACTORS:
- Every wrong answer must be plausible on first read — a student who read the passage carelessly should be tempted by it
- Use these specific trap types: (a) true statement that doesn't answer the question, (b) answer that partially matches then goes wrong, (c) answer using extreme language like "always"/"never"/"all" when the passage is nuanced, (d) answer that confuses two things the passage actually mentions
- All four choices must be similar in length and grammatical structure — never make the correct answer obviously longer or more hedged

LANGUAGE:
- Never use outside knowledge — every correct answer must be 100% defensible from the passage alone
- No answer choice should begin with the same 3 words as another choice in the same question
- Vary sentence structure across choices

EXPLANATIONS:
- For the correct answer: quote or closely paraphrase the specific sentence(s) from the passage that support it
- For each wrong answer: name the trap type and explain why it fails (e.g., "This is true but answers a different question" or "This overstates — the author says X, not Y")

━━━ OUTPUT FORMAT ━━━

Return ONLY valid JSON — no markdown, no extra text:
{{
  "questions": [
    {{
      "question": "Question stem here",
      "choices": {{
        "A": "...",
        "B": "...",
        "C": "...",
        "D": "..."
      }},
      "correct": "A",
      "explanation": "Correct: A is supported by [quote from passage]. Wrong: B is a too-extreme version of what the author says. C confuses X with Y from paragraph 2. D is never mentioned in the passage."
    }}
  ]
}}"""


def generate_questions(passage_data: dict):
    """Given passage data dict, return list of 5 question dicts."""
    prompt = PROMPT.format(
        passage=passage_data["passage"],
        source_title=passage_data.get("source_title", ""),
        source_name=passage_data.get("source_name", ""),
    )

    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()

    # Strip markdown fences if present
    if "```" in raw:
        parts = raw.split("```")
        # Find the json block
        for part in parts:
            part = part.strip()
            if part.startswith("json"):
                part = part[4:].strip()
            if part.startswith("{"):
                raw = part
                break
    raw = raw.strip()

    # Find the outermost JSON object in case there's leading/trailing text
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start != -1 and end > start:
        raw = raw[start:end]

    data = json.loads(raw)
    return data["questions"]
