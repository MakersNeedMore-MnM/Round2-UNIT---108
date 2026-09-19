"""
Agent 8 — Plain Language Translator
Converts legal clause text into clear, Grade-8 level English.
"""
import json, re
from typing import List, Dict
from utils.llm_client import chat


def translate_to_plain(clauses: List[Dict], client) -> List[Dict]:
    """Add plain_english field to every clause."""
    # Only translate non-trivial clauses
    to_translate = [c for c in clauses if len(c["text"].split()) > 10]

    for i in range(0, len(to_translate), 8):
        batch = to_translate[i:i+8]
        _translate_batch(batch, client)

    for c in clauses:
        if not c.get("plain_english"):
            c["plain_english"] = c["text"][:200]
    return clauses


def _translate_batch(batch: List[Dict], client):
    items = "\n\n".join(
        f'[{c["id"]}]: {c["text"][:600]}' for c in batch
    )

    prompt = f"""You are a plain-language legal expert. Translate each legal clause into simple English that anyone can understand (Grade 8 reading level).

Rules:
- Use short sentences
- Avoid legal jargon
- Explain what it means for the signing party
- Keep it under 60 words per clause

Return a JSON array:
[{{"id": "clause id", "plain_english": "simple explanation"}}]

Legal clauses:
{items}

Return ONLY valid JSON array."""

    try:
        response = chat(client, [{"role": "user", "content": prompt}], temperature=0.3)
        response = re.sub(r"```[a-z]*\n?", "", response).replace("```", "").strip()
        results = json.loads(response)
        res_map = {r["id"]: r for r in results}
        for clause in batch:
            if clause["id"] in res_map:
                clause["plain_english"] = res_map[clause["id"]].get("plain_english", "")
    except Exception:
        for clause in batch:
            clause["plain_english"] = _simple_translate(clause["text"])


def _simple_translate(text: str) -> str:
    """Ultra-simple fallback."""
    words = text.split()
    short = " ".join(words[:40])
    return short + ("..." if len(words) > 40 else "")
