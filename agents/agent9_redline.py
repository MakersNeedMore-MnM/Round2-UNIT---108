"""
Agent 9 — Redlining Agent
Suggests safer clause rewrites and negotiation strategies for risky clauses.
"""
import json, re
from typing import List, Dict
from utils.llm_client import chat
from data.templates import STANDARD_TEMPLATES


def generate_redlines(clauses: List[Dict], client) -> List[Dict]:
    """Add redline_suggestion and negotiation_tip to HIGH/MEDIUM risk clauses."""
    target = [c for c in clauses if c.get("risk_level") in ("HIGH", "MEDIUM")]

    for i in range(0, len(target), 5):
        batch = target[i:i+5]
        _redline_batch(batch, client)

    for c in clauses:
        if not c.get("redline_suggestion"):
            c["redline_suggestion"] = ""
        if not c.get("negotiation_tip"):
            c["negotiation_tip"] = ""
    return clauses


def _redline_batch(batch: List[Dict], client):
    items = []
    for c in batch:
        cat = c.get("category", "General / Miscellaneous")
        std = STANDARD_TEMPLATES.get(cat, {}).get("standard", "")
        items.append(
            f'[{c["id"]}] Category: {cat}\n'
            f'Issue: {c.get("risk_issue","")}\n'
            f'Original: {c["text"][:500]}\n'
            f'Standard reference: {std[:300]}'
        )

    prompt = f"""You are a contract negotiation specialist. For each risky clause, provide:
1. A safer rewrite (redline) that protects the reviewing party
2. A negotiation tip — practical advice on how to negotiate this change

Return a JSON array:
[{{
  "id": "clause id",
  "redline_suggestion": "improved clause text, 2-4 sentences",
  "negotiation_tip": "practical negotiation advice, 1-2 sentences"
}}]

Clauses to redline:
{"=" * 40 + chr(10) + (chr(10) + "=" * 40 + chr(10)).join(items)}

Return ONLY valid JSON array."""

    try:
        response = chat(client, [{"role": "user", "content": prompt}], temperature=0.3)
        response = re.sub(r"```[a-z]*\n?", "", response).replace("```", "").strip()
        results = json.loads(response)
        res_map = {r["id"]: r for r in results}
        for clause in batch:
            if clause["id"] in res_map:
                clause["redline_suggestion"] = res_map[clause["id"]].get("redline_suggestion", "")
                clause["negotiation_tip"] = res_map[clause["id"]].get("negotiation_tip", "")
    except Exception:
        cat_defaults = {
            "Liability": "Add a mutual liability cap of 2x the total contract value. Exclude consequential and indirect damages for both parties.",
            "Termination": "Ensure mutual 30-day written notice for convenience termination. Add a 15-day cure period for breach.",
            "Payment Terms": "Specify Net 30 payment terms. Cap late fees at 1.5% per month.",
            "Confidentiality": "Make obligations mutual. Add a 3-year survival clause post-termination.",
            "IP Ownership": "Client should own all deliverables. Vendor retains background IP with a license grant.",
            "Indemnity": "Make indemnification mutual. Add gross-negligence threshold and cap it at the liability limit.",
        }
        for clause in batch:
            cat = clause.get("category", "")
            clause["redline_suggestion"] = cat_defaults.get(cat, "Consult legal counsel to review and redraft this clause.")
            clause["negotiation_tip"] = "Request a markup from your legal team before signing. Do not accept this clause as-is."
