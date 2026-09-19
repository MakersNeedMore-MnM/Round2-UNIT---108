"""
Agent 2 — Clause Segmenter
Splits raw contract text into atomic, numbered clauses.
Uses regex heuristics first; falls back to LLM for unstructured contracts.
"""
import re
import json
from typing import List, Dict, Any
from utils.llm_client import chat


# Patterns that typically mark a new clause / section
_CLAUSE_PATTERNS = [
    r'^\s*(\d+[\.\)]\d*[\.\)]?\d*)\s+[A-Z]',          # 1. 1.1 1.1.1
    r'^\s*(ARTICLE|SECTION|CLAUSE|SCHEDULE|EXHIBIT)\s+[IVXLC\d]+',
    r'^\s*([A-Z][A-Z\s]{3,})\s*[\n:]',                  # ALL-CAPS headings
    r'^\s*\([a-z]\)\s',                                  # (a) (b)
]
_COMPILED = [re.compile(p, re.MULTILINE) for p in _CLAUSE_PATTERNS]


def segment_clauses(raw_text: str, client, use_llm: bool = True) -> List[Dict[str, Any]]:
    """Return list of clause dicts with id, text, position."""
    clauses = _regex_segment(raw_text)

    # If regex finds too few clauses, use LLM to help
    if len(clauses) < 3 and use_llm and client:
        clauses = _llm_segment(raw_text, client)

    # Deduplicate very short segments
    clauses = [c for c in clauses if len(c["text"].split()) >= 8]

    # Re-number cleanly
    for i, c in enumerate(clauses):
        c["id"] = f"C{i+1:03d}"
        c["position"] = i + 1

    return clauses


def _regex_segment(text: str) -> List[Dict[str, Any]]:
    """Split on section-header lines."""
    # Find all positions where a new clause starts
    split_points = set()
    for pattern in _COMPILED:
        for m in pattern.finditer(text):
            split_points.add(m.start())

    if not split_points:
        # Fallback: split on double newline paragraphs
        parts = re.split(r'\n\n+', text)
        return [{"id": "", "text": p.strip(), "position": i} for i, p in enumerate(parts) if p.strip()]

    split_points = sorted(split_points)
    clauses = []
    for idx, start in enumerate(split_points):
        end = split_points[idx + 1] if idx + 1 < len(split_points) else len(text)
        snippet = text[start:end].strip()
        if snippet:
            clauses.append({"id": "", "text": snippet, "position": idx})

    return clauses


def _llm_segment(text: str, client) -> List[Dict[str, Any]]:
    """Ask LLM to identify and number clauses."""
    prompt = f"""You are a legal document segmenter. Split the following contract text into individual clauses.

Return ONLY a JSON array where each element has:
- "id": sequential string like "C001"
- "text": the full clause text
- "position": integer starting at 1

Contract text:
{text[:8000]}

Return valid JSON only, no markdown fences."""

    try:
        response = chat(client, [{"role": "user", "content": prompt}], temperature=0.1)
        response = response.strip()
        if response.startswith("```"):
            response = re.sub(r"```[a-z]*\n?", "", response).replace("```", "")
        data = json.loads(response)
        return data if isinstance(data, list) else []
    except Exception:
        # Final fallback
        parts = text.split("\n\n")
        return [{"id": f"C{i+1:03d}", "text": p.strip(), "position": i + 1}
                for i, p in enumerate(parts) if len(p.split()) >= 8]
