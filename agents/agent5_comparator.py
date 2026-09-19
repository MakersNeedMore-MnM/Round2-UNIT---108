"""
Agent 5 — Template Comparator (RAG-based)
Compares each clause against standard templates using keyword matching + LLM semantic diff.
"""
import json, re
from typing import List, Dict
from utils.llm_client import chat
from data.templates import STANDARD_TEMPLATES


def compare_with_templates(clauses: List[Dict], client) -> List[Dict]:
    """Add template_deviation and deviation_score to each clause."""
    for clause in clauses:
        cat = clause.get("category", "General / Miscellaneous")
        template = STANDARD_TEMPLATES.get(cat, STANDARD_TEMPLATES["General / Miscellaneous"])
        deviation, score = _compare_clause(clause["text"], template, cat, client)
        clause["template_deviation"] = deviation
        clause["deviation_score"] = score
    return clauses


def _compare_clause(clause_text: str, template: Dict, category: str, client) -> tuple:
    standard_text = template["standard"]
    key_elements = template["key_elements"]
    red_flags = template["red_flags"]

    prompt = f"""You are a legal contract analyst comparing a contract clause against an industry-standard template.

CATEGORY: {category}

STANDARD TEMPLATE:
{standard_text}

KEY ELEMENTS that should be present: {json.dumps(key_elements)}
RED FLAGS to watch for: {json.dumps(red_flags)}

ACTUAL CONTRACT CLAUSE:
{clause_text[:1500]}

Analyze and return ONLY valid JSON:
{{
  "deviation_summary": "1-2 sentence description of what differs from the standard",
  "missing_elements": ["element missing from actual clause"],
  "red_flags_found": ["red flags present in actual clause"],
  "deviation_score": 0.0,
  "compliant": true
}}

deviation_score: 0.0 = fully compliant, 1.0 = completely non-compliant.
Return valid JSON only."""

    try:
        response = chat(client, [{"role": "user", "content": prompt}], temperature=0.1)
        response = re.sub(r"```[a-z]*\n?", "", response).replace("```", "").strip()
        data = json.loads(response)
        summary = data.get("deviation_summary", "No significant deviation detected.")
        if data.get("missing_elements"):
            summary += f" Missing: {', '.join(data['missing_elements'][:3])}."
        if data.get("red_flags_found"):
            summary += f" Red flags: {', '.join(data['red_flags_found'][:2])}."
        score = float(data.get("deviation_score", 0.2))
        return summary, score
    except Exception:
        # Fallback keyword check
        text_lower = clause_text.lower()
        flags_found = [f for f in red_flags if any(w in text_lower for w in f.lower().split()[:2])]
        missing = [e for e in key_elements if not any(w in text_lower for w in e.lower().split()[:2])]
        score = min(1.0, len(flags_found) * 0.3 + len(missing) * 0.15)
        summary = f"Keyword analysis: {len(flags_found)} red flags found, {len(missing)} key elements possibly missing."
        return summary, score
