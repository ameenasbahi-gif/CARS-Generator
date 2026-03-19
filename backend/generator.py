"""
Uses Claude to generate MCAT CARS-style questions and explanations
for a scraped passage.
"""

import anthropic
import json

client = anthropic.Anthropic()

PROMPT = """You are an expert MCAT CARS question writer. Given the passage below, generate exactly 5 MCAT-style questions with answer choices and explanations.

PASSAGE:
{passage}

SOURCE: {source_title} ({source_name})

Return ONLY valid JSON — no markdown, no extra text — in this exact format:
{{
  "questions": [
    {{
      "question": "Question text",
      "choices": {{
        "A": "...",
        "B": "...",
        "C": "...",
        "D": "..."
      }},
      "correct": "A",
      "explanation": "Explain why A is correct and why B, C, D are wrong. Reference specific parts of the passage."
    }}
  ]
}}

Question types to include (one each):
1. Main idea / primary purpose of the passage
2. Author's tone, attitude, or perspective
3. Inference — what can be concluded from the passage
4. Specific detail or textual evidence
5. Application — how would the author respond to a new scenario

Make wrong answers plausible but clearly incorrect on careful reading. Base everything strictly on the passage text."""


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
