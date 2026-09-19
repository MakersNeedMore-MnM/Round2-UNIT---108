"""
Agent 7 — Legal Reasoner
Chain-of-thought legal impact analysis for HIGH and MEDIUM risk clauses.
"""
import json, re
from typing import List, Dict
from utils.llm_client import chat


def legal_reasoning(clauses: List[Dict], client) -> List[Dict]:
    """Add legal_reasoning field to HIGH/MEDIUM risk clauses."""
    target = [c for c in clauses if c.get("risk_level") in ("HIGH", "MEDIUM")]
    if not target or not client:
        for c in clauses:
            if not c.get("legal_reasoning"):
                c["legal_reasoning"] = ""
        return clauses

    # Batch in groups of 5
    for i in range(0, len(target), 5):
        batch = target[i:i+5]
        _reason_batch(batch, client)

    # Ensure all clauses have the field
    for c in clauses:
        if not c.get("legal_reasoning"):
            c["legal_reasoning"] = ""
    return clauses


def _reason_batch(batch: List[Dict], client):
    items = "\n\n".join(
        f'[{c["id"]}] Category: {c["category"]} | Risk: {c["risk_level"]}\n'
        f'Issue: {c.get("risk_issue","")}\n'
        f'Clause text: {c["text"][:700]}'
        for c in batch
    )

    prompt = f"""You are a senior legal counsel providing chain-of-thought analysis of risky contract clauses.

For each clause, reason step-by-step:
1. What exactly is the legal problem?
2. What is the business/financial exposure?
3. What precedent or legal principle applies?
4. What is the worst-case scenario?

Return a JSON array:
[{{
  "id": "clause id",
  "legal_reasoning": "3-4 sentence detailed legal analysis"
}}]

Clauses:
{items}

Return ONLY valid JSON array."""

    try:
        response = chat(client, [{"role": "user", "content": prompt}], temperature=0.2)
        response = re.sub(r"```[a-z]*\n?", "", response).replace("```", "").strip()
        results = json.loads(response)
        res_map = {r["id"]: r for r in results}
        for clause in batch:
            if clause["id"] in res_map:
                clause["legal_reasoning"] = res_map[clause["id"]].get("legal_reasoning", "")
    except Exception:
        for clause in batch:
            clause["legal_reasoning"] = (
                f"This {clause.get('category','clause')} clause presents a {clause.get('risk_level','potential')} "
                f"risk due to: {clause.get('risk_issue','')}. "
                f"Potential impact: {clause.get('risk_impact','')}."
            )
