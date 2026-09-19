"""
Agent 3 — Clause Classifier
Tags each clause with one of 10 legal categories + confidence score.
Uses batch LLM call for efficiency.
"""
import json
import re
from typing import List, Dict, Any
from utils.llm_client import chat

LEGAL_CATEGORIES = [
    "Liability",
    "Termination",
    "Payment Terms",
    "Confidentiality",
    "IP Ownership",
    "Indemnity",
    "Dispute Resolution",
    "Force Majeure",
    "Warranties",
    "General / Miscellaneous",
]

BATCH_SIZE = 10


def classify_clauses(clauses: List[Dict], client) -> List[Dict]:
    """Return clauses with 'category' and 'confidence' fields added."""
    results = []
    for i in range(0, len(clauses), BATCH_SIZE):
        batch = clauses[i:i + BATCH_SIZE]
        classified = _classify_batch(batch, client)
        results.extend(classified)
    return results


def _classify_batch(batch: List[Dict], client) -> List[Dict]:
    items = "\n\n".join(
        f'[{c["id"]}]: {c["text"][:400]}' for c in batch
    )

    prompt = f"""You are a legal clause classifier. Classify each clause below into exactly one category from this list:
{json.dumps(LEGAL_CATEGORIES, indent=2)}

For each clause, return a JSON array element with:
- "id": the clause ID given
- "category": one of the categories above
- "confidence": float 0.0-1.0

Clauses:
{items}

Return ONLY a valid JSON array. No markdown, no explanation."""

    try:
        response = chat(client, [{"role": "user", "content": prompt}], temperature=0.1)
        response = re.sub(r"```[a-z]*\n?", "", response).replace("```", "").strip()
        classifications = json.loads(response)
        class_map = {c["id"]: c for c in classifications}
        for clause in batch:
            info = class_map.get(clause["id"], {})
            clause["category"] = info.get("category", "General / Miscellaneous")
            clause["confidence"] = float(info.get("confidence", 0.7))
    except Exception:
        for clause in batch:
            clause["category"] = _keyword_classify(clause["text"])
            clause["confidence"] = 0.6
    return batch


def _keyword_classify(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ["liab", "damage", "indemnif"]):
        return "Liability"
    if any(w in t for w in ["terminat", "expir", "cancel"]):
        return "Termination"
    if any(w in t for w in ["payment", "invoice", "fee", "price", "cost"]):
        return "Payment Terms"
    if any(w in t for w in ["confidential", "secret", "nda", "disclos"]):
        return "Confidentiality"
    if any(w in t for w in ["intellectual property", "patent", "copyright", "trademark", "ip "]):
        return "IP Ownership"
    if any(w in t for w in ["indemnif", "hold harmless"]):
        return "Indemnity"
    if any(w in t for w in ["arbitrat", "dispute", "jurisdiction", "governing law"]):
        return "Dispute Resolution"
    if any(w in t for w in ["force majeure", "act of god", "unforeseen"]):
        return "Force Majeure"
    if any(w in t for w in ["warrant", "represent", "guarantee"]):
        return "Warranties"
    return "General / Miscellaneous"
