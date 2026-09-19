"""
ContractState — shared state object flowing through the LangGraph pipeline.
Every agent reads from and writes into this TypedDict.
"""
from typing import TypedDict, List, Dict, Any, Optional


class Clause(TypedDict):
    id: str
    text: str
    position: int
    category: str
    confidence: float
    key_fields: Dict[str, Any]
    template_deviation: Optional[str]
    deviation_score: float          # 0-1, higher = bigger deviation
    risk_level: str                 # HIGH / MEDIUM / LOW / NONE
    risk_issue: str
    risk_impact: str
    legal_reasoning: str
    plain_english: str
    redline_suggestion: str
    negotiation_tip: str


class ContractState(TypedDict):
    # inputs
    filename: str
    raw_text: str
    api_key: str

    # pipeline outputs
    clauses: List[Clause]
    extracted_metadata: Dict[str, Any]   # parties, dates, amounts
    risk_score: int                       # 0-100
    risk_breakdown: Dict[str, str]        # financial/legal/operational
    executive_summary: str
    plain_summary: str
    recommendations: List[str]
    report_ready: bool
    error: Optional[str]
