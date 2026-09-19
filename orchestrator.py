"""
Orchestrator — LangGraph-style pipeline connecting all 10 agents.
No API key parameter anywhere — client created once via st.secrets.
"""
from typing import Dict, Any, Generator
from utils.llm_client import get_client
from agents.agent1_parser    import parse_document
from agents.agent2_segmenter import segment_clauses
from agents.agent3_classifier import classify_clauses
from agents.agent4_extractor  import extract_key_info
from agents.agent5_comparator import compare_with_templates
from agents.agent6_risk       import detect_risks
from agents.agent7_reasoner   import legal_reasoning
from agents.agent8_plain      import translate_to_plain
from agents.agent9_redline    import generate_redlines
from agents.agent10_report    import generate_summaries

PIPELINE_STEPS = [
    ("🔍 Parsing document...",               "Document Parser"),
    ("✂️  Segmenting clauses...",            "Clause Segmenter"),
    ("🏷️  Classifying clause types...",      "Clause Classifier"),
    ("📋 Extracting key information...",     "Key Info Extractor"),
    ("📊 Comparing with templates (RAG)...", "Template Comparator"),
    ("⚠️  Detecting risks...",              "Risk Detector"),
    ("⚖️  Legal reasoning analysis...",      "Legal Reasoner"),
    ("💬 Translating to plain English...",   "Plain Language Agent"),
    ("✏️  Generating redlines...",           "Redlining Agent"),
    ("📄 Building final report...",          "Report Generator"),
]


def run_pipeline(file_bytes: bytes, filename: str) -> Generator[Dict[str, Any], None, None]:
    """Yields progress dicts; last yield contains full state in 'state' key."""
    state: Dict[str, Any] = {
        "filename": filename,
        "raw_text": "",
        "clauses": [],
        "extracted_metadata": {},
        "risk_score": 0,
        "risk_breakdown": {},
        "executive_summary": "",
        "plain_summary": "",
        "recommendations": [],
        "report_ready": False,
        "error": None,
    }

    client = get_client()
    total  = len(PIPELINE_STEPS)

    def prog(i, msg=""):
        label, agent = PIPELINE_STEPS[i]
        return {"step": i+1, "total": total, "label": msg or label,
                "agent": agent, "pct": int(((i+1)/total)*100), "state": None}

    try:
        # 1 — Parse
        yield prog(0)
        raw_text, meta = parse_document(file_bytes, filename)
        state["raw_text"] = raw_text
        state["extracted_metadata"].update(meta)

        # 2 — Segment
        yield prog(1)
        raw_clauses = segment_clauses(raw_text, client)
        state["clauses"] = [
            {"id": c["id"], "text": c["text"], "position": c["position"],
             "category": "", "confidence": 0.0, "key_fields": {},
             "template_deviation": None, "deviation_score": 0.0,
             "risk_level": "NONE", "risk_issue": "", "risk_impact": "",
             "legal_reasoning": "", "plain_english": "",
             "redline_suggestion": "", "negotiation_tip": ""}
            for c in raw_clauses
        ]

        # 3 — Classify
        yield prog(2)
        state["clauses"] = classify_clauses(state["clauses"], client)

        # 4 — Extract
        yield prog(3)
        state["extracted_metadata"].update(extract_key_info(raw_text, client))

        # 5 — Template comparison
        yield prog(4)
        state["clauses"] = compare_with_templates(state["clauses"], client)

        # 6 — Risk detection
        yield prog(5)
        state["clauses"], state["risk_score"], state["risk_breakdown"] = \
            detect_risks(state["clauses"], client)

        # 7 — Legal reasoning
        yield prog(6)
        state["clauses"] = legal_reasoning(state["clauses"], client)

        # 8 — Plain language
        yield prog(7)
        state["clauses"] = translate_to_plain(state["clauses"], client)

        # 9 — Redlines
        yield prog(8)
        state["clauses"] = generate_redlines(state["clauses"], client)

        # 10 — Summaries + report
        yield prog(9)
        state = generate_summaries(state, client)

        yield {"step": total, "total": total, "label": "✅ Analysis complete!",
               "agent": "Orchestrator", "pct": 100, "state": state}

    except Exception as e:
        import traceback
        state["error"] = f"{e}\n\n{traceback.format_exc()}"
        yield {"step": 0, "total": total, "label": f"❌ Error: {e}",
               "agent": "Orchestrator", "pct": 0, "state": state}
