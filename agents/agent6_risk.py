"""
Agent 6 — Risk Detector
Assigns HIGH / MEDIUM / LOW / NONE risk to each clause using hybrid rule + LLM engine.
Also computes overall contract risk score 0-100.
"""
import json, re
from typing import List, Dict, Tuple
from utils.llm_client import chat

# Rule-based risk triggers
HIGH_RISK_TRIGGERS = [
    "unlimited liability", "no cap on damages", "unconditional indemnif",
    "irrevocable license", "unilateral termination", "immediate termination",
    "waive all claims", "no cure period", "perpetual license", "assign this agreement",
    "sole discretion", "without notice", "all intellectual property shall vest",
]
MEDIUM_RISK_TRIGGERS = [
    "reasonable", "may terminate", "at our discretion", "subject to change",
    "automatic renewal", "deemed acceptance", "best efforts", "reasonable notice",
    "partial ownership", "joint ownership",
]
LOW_RISK_TRIGGERS = [
    "minor variation", "clerical", "schedule", "exhibit", "appendix",
]

RISK_WEIGHTS = {"HIGH": 25, "MEDIUM": 10, "LOW": 3, "NONE": 0}


def detect_risks(clauses: List[Dict], client) -> Tuple[List[Dict], int, Dict]:
    """Return (clauses_with_risk, risk_score_0_100, risk_breakdown)."""
    # Quick rule-based pass
    for clause in clauses:
        clause = _rule_based_risk(clause)

    # LLM-enhanced pass for clauses flagged HIGH/MEDIUM or high deviation
    high_medium = [c for c in clauses if c.get("risk_level") in ("HIGH", "MEDIUM") or c.get("deviation_score", 0) > 0.5]
    if high_medium and client:
        clauses = _llm_risk_enhance(clauses, high_medium, client)

    # Score
    score, breakdown = _compute_score(clauses)
    return clauses, score, breakdown


def _rule_based_risk(clause: Dict) -> Dict:
    text_lower = clause["text"].lower()
    dev_score = clause.get("deviation_score", 0.0)

    if any(t in text_lower for t in HIGH_RISK_TRIGGERS) or dev_score >= 0.7:
        clause["risk_level"] = "HIGH"
        matched = [t for t in HIGH_RISK_TRIGGERS if t in text_lower]
        clause["risk_issue"] = matched[0] if matched else "High deviation from standard template"
        clause["risk_impact"] = "Significant financial or legal exposure"
    elif any(t in text_lower for t in MEDIUM_RISK_TRIGGERS) or dev_score >= 0.4:
        clause["risk_level"] = "MEDIUM"
        matched = [t for t in MEDIUM_RISK_TRIGGERS if t in text_lower]
        clause["risk_issue"] = matched[0] if matched else "Moderate deviation from standard template"
        clause["risk_impact"] = "Potential operational or legal risk"
    elif any(t in text_lower for t in LOW_RISK_TRIGGERS) or dev_score >= 0.1:
        clause["risk_level"] = "LOW"
        clause["risk_issue"] = "Minor wording variation"
        clause["risk_impact"] = "Minimal risk"
    else:
        clause["risk_level"] = "NONE"
        clause["risk_issue"] = ""
        clause["risk_impact"] = ""

    return clause


def _llm_risk_enhance(all_clauses: List[Dict], target_clauses: List[Dict], client) -> List[Dict]:
    """Use LLM to refine risk assessment for flagged clauses."""
    items = "\n\n".join(
        f'[{c["id"]}] ({c["category"]}):\n{c["text"][:600]}' for c in target_clauses
    )
    prompt = f"""You are a senior legal risk analyst. Evaluate these contract clauses for legal and financial risk.

For each clause return a JSON array element:
{{
  "id": "clause id",
  "risk_level": "HIGH" | "MEDIUM" | "LOW" | "NONE",
  "risk_issue": "specific issue in 8 words or less",
  "risk_impact": "business impact in 10 words or less"
}}

Clauses to evaluate:
{items}

Return ONLY a valid JSON array."""

    try:
        response = chat(client, [{"role": "user", "content": prompt}], temperature=0.1)
        response = re.sub(r"```[a-z]*\n?", "", response).replace("```", "").strip()
        assessments = json.loads(response)
        assess_map = {a["id"]: a for a in assessments}
        for clause in all_clauses:
            if clause["id"] in assess_map:
                a = assess_map[clause["id"]]
                clause["risk_level"] = a.get("risk_level", clause["risk_level"])
                clause["risk_issue"] = a.get("risk_issue", clause["risk_issue"])
                clause["risk_impact"] = a.get("risk_impact", clause["risk_impact"])
    except Exception:
        pass
    return all_clauses


def _compute_score(clauses: List[Dict]) -> Tuple[int, Dict]:
    total = 0
    counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    cat_risks = {"financial": [], "legal": [], "operational": []}

    FINANCIAL_CATS = {"Liability", "Payment Terms", "Indemnity"}
    LEGAL_CATS = {"IP Ownership", "Confidentiality", "Dispute Resolution", "Warranties"}
    OP_CATS = {"Termination", "Force Majeure", "General / Miscellaneous"}

    for c in clauses:
        lvl = c.get("risk_level", "NONE")
        counts[lvl] = counts.get(lvl, 0) + 1
        total += RISK_WEIGHTS.get(lvl, 0)
        cat = c.get("category", "")
        if cat in FINANCIAL_CATS:
            cat_risks["financial"].append(lvl)
        elif cat in LEGAL_CATS:
            cat_risks["legal"].append(lvl)
        else:
            cat_risks["operational"].append(lvl)

    # Normalise to 0-100
    max_possible = len(clauses) * 25 if clauses else 1
    score = min(100, int((total / max_possible) * 100))

    def dim_rating(risks):
        if "HIGH" in risks:
            return "High"
        if "MEDIUM" in risks:
            return "Medium"
        if "LOW" in risks:
            return "Low"
        return "Low"

    breakdown = {
        "financial": dim_rating(cat_risks["financial"]),
        "legal": dim_rating(cat_risks["legal"]),
        "operational": dim_rating(cat_risks["operational"]),
        "high_count": counts["HIGH"],
        "medium_count": counts["MEDIUM"],
        "low_count": counts["LOW"],
    }
    return score, breakdown
