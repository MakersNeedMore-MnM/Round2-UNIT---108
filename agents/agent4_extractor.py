"""
Agent 4 — Key Information Extractor
FIXED: simpler prompt, better JSON parsing, debug logging, fallback keyword extraction
"""
import json
import re
from typing import Dict, Any
from utils.llm_client import chat


def extract_key_info(raw_text: str, client) -> Dict[str, Any]:
    """Return structured metadata dict from full contract text."""

    # Use first 10000 chars — enough for any contract header + key clauses
    text_sample = raw_text[:10000]

    # ── Step 1: Try LLM extraction ─────────────────────────────────────────
    prompt = f"""Extract key information from this legal contract. Return ONLY a JSON object, nothing else.

Required JSON format:
{{
  "contract_type": "type of contract e.g. Employment Agreement",
  "parties": {{
    "party_a": "first company or person name",
    "party_b": "second company or person name",
    "other_parties": []
  }},
  "effective_date": "date contract starts",
  "expiry_date": "date contract ends or Not specified",
  "contract_value": "monetary value e.g. INR 5,00,000 per month",
  "payment_terms": "how payment is made e.g. Net 30 days",
  "late_penalty": "penalty for late payment e.g. 2% per month",
  "termination_notice": "notice period required e.g. 30 days",
  "governing_law": "which country or state law applies",
  "key_obligations_party_a": ["list", "of", "obligations"],
  "key_obligations_party_b": ["list", "of", "obligations"],
  "important_dates": [{{"label": "name", "date": "value"}}]
}}

Rules:
- If a field is truly not mentioned, use "Not specified" (NOT "Unknown")
- For employment contracts: party_a=Company, party_b=Employee, contract_value=salary
- For NDAs: party_a=Disclosing Party, party_b=Receiving Party
- For vendor/service: party_a=Client, party_b=Vendor, contract_value=fee amount
- Extract ACTUAL values from the text — do not guess

CONTRACT TEXT:
{text_sample}

JSON only, no explanation, no markdown:"""

    llm_result = None
    try:
        response = chat(client, [{"role": "user", "content": prompt}], temperature=0.0, max_tokens=2000)
        # Strip markdown fences if present
        response = re.sub(r'```(?:json)?\s*', '', response).strip()
        response = response.replace('```', '').strip()
        # Find the JSON object
        match = re.search(r'\{[\s\S]*\}', response)
        if match:
            llm_result = json.loads(match.group(0))
    except Exception as e:
        llm_result = None

    # ── Step 2: Keyword fallback to fill any "Unknown" / missing fields ────
    keyword_result = _keyword_extract(raw_text)

    # ── Step 3: Merge — LLM wins unless it returned Unknown/None ──────────
    final = keyword_result.copy()
    if llm_result and isinstance(llm_result, dict):
        for key, val in llm_result.items():
            if key == "parties" and isinstance(val, dict):
                for pk, pv in val.items():
                    if pv and str(pv).lower() not in ("unknown", "not found", "n/a", "none", ""):
                        final["parties"][pk] = pv
            elif val and str(val).lower() not in ("unknown", "not found", "n/a", "none", ""):
                final[key] = val

    return final


def _keyword_extract(text: str) -> Dict[str, Any]:
    """
    Regex-based keyword extraction as reliable fallback.
    Catches parties, dates, amounts, governing law from raw text.
    """
    t = text

    result = {
        "contract_type": "Unknown",
        "parties": {"party_a": "Unknown", "party_b": "Unknown", "other_parties": []},
        "effective_date": "Not specified",
        "expiry_date": "Not specified",
        "contract_value": "Not specified",
        "payment_terms": "Not specified",
        "late_penalty": "Not specified",
        "termination_notice": "Not specified",
        "governing_law": "Not specified",
        "key_obligations_party_a": [],
        "key_obligations_party_b": [],
        "important_dates": [],
    }

    # Contract type from title
    type_patterns = [
        (r'(?i)(non.?disclosure agreement|nda)',              "Non-Disclosure Agreement"),
        (r'(?i)(employment agreement|employment contract)',    "Employment Agreement"),
        (r'(?i)(vendor.*agreement|service.*agreement)',        "Vendor / Service Agreement"),
        (r'(?i)(software.*development.*agreement)',            "Software Development Agreement"),
        (r'(?i)(consultancy.*agreement|consulting.*agreement)',"Consultancy Agreement"),
        (r'(?i)(lease.*agreement|rental.*agreement)',          "Lease Agreement"),
        (r'(?i)(partnership.*agreement)',                      "Partnership Agreement"),
    ]
    for pat, label in type_patterns:
        if re.search(pat, t):
            result["contract_type"] = label
            break

    # Parties — "between X ... and Y"
    between = re.search(
        r'(?i)between\s+([\w\s,\.]+?(?:Ltd|Limited|LLP|Pvt|Inc|Corp|Private|Solutions|Technologies|Enterprises)[\.]*[\w\s]*?)\s*[,\(].*?and\s+([\w\s,\.]+?(?:Ltd|Limited|LLP|Pvt|Inc|Corp|Private|Solutions|Technologies|Enterprises|Ms\.|Mr\.|Mrs\.)[\.]*[\w\s]*?)\s*[,\(]',
        t
    )
    if between:
        result["parties"]["party_a"] = between.group(1).strip()
        result["parties"]["party_b"] = between.group(2).strip()
    else:
        # Try simpler: "between A and B"
        between2 = re.search(r'(?i)between\s+(.{5,60}?)\s+and\s+(.{5,60}?)[\.\n,\(]', t)
        if between2:
            result["parties"]["party_a"] = between2.group(1).strip()
            result["parties"]["party_b"] = between2.group(2).strip()

    # Effective date patterns
    date_patterns = [
        r'(?i)(?:entered into|made|dated?|effective)\s+(?:as of|on)?\s*(\d{1,2}(?:st|nd|rd|th)?\s+\w+\s+\d{4})',
        r'(?i)(?:entered into|made|dated?|effective)\s+(?:as of|on)?\s*(\w+\s+\d{1,2},?\s+\d{4})',
        r'(?i)as of\s+(\w+\s+\d{1,2},?\s+\d{4})',
        r'(?i)dated\s+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
    ]
    for pat in date_patterns:
        m = re.search(pat, t)
        if m:
            result["effective_date"] = m.group(1).strip()
            break

    # Start date for employment
    start = re.search(r'(?i)(?:start date|commencement date|joining date)[^\n]*?(\w+\s+\d{1,2},?\s+\d{4}|\d{1,2}\s+\w+\s+\d{4})', t)
    if start:
        result["important_dates"].append({"label": "Start Date", "date": start.group(1).strip()})

    # Contract value / salary
    value_patterns = [
        r'(?i)(?:salary|remuneration|fee|retainer|contract value)[^\n]*?((?:INR|USD|EUR|GBP|Rs\.?)\s*[\d,]+(?:\s*(?:lakhs?|lacs?|per\s+(?:month|annum|year)))?)',
        r'(?i)((?:INR|USD|EUR|Rs\.?)\s*[\d,]+(?:\s*(?:lakhs?|lacs?|crores?|per\s+(?:month|annum|year)))?)',
    ]
    for pat in value_patterns:
        m = re.search(pat, t)
        if m:
            result["contract_value"] = m.group(1).strip()
            break

    # Payment terms
    pay = re.search(r'(?i)(?:payment|paid)[^\n]*?(net\s*\d+|within\s+\d+\s+days?|monthly|last\s+working\s+day)', t)
    if pay:
        result["payment_terms"] = pay.group(1).strip()

    # Late penalty
    penalty = re.search(r'(?i)(?:late|overdue|interest)[^\n]*?(\d+(?:\.\d+)?%\s*(?:per\s+(?:month|annum|year))?)', t)
    if penalty:
        result["late_penalty"] = penalty.group(1).strip()

    # Termination notice
    notice = re.search(r'(?i)(?:terminat|notice)[^\n]*?(\d+)\s*(days?|months?|weeks?)\s*(?:written\s+)?notice', t)
    if notice:
        result["termination_notice"] = f"{notice.group(1)} {notice.group(2)}"

    # Governing law
    law_patterns = [
        r'(?i)governed by[^\n]*?laws?\s+of\s+([\w\s,]+?)(?:\.|,|\n|without)',
        r'(?i)governing law[^\n]*?(India|United States|Delaware|England|Singapore|UAE|Australia)',
        r'(?i)laws?\s+of\s+(?:the\s+)?(India|United States|Delaware|England|Singapore|UAE)',
    ]
    for pat in law_patterns:
        m = re.search(pat, t)
        if m:
            result["governing_law"] = m.group(1).strip()
            break

    return result