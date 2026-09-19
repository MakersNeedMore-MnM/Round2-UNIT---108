"""Page: Chat Assistant — Q&A about the analysed contract

"""
import streamlit as st
from utils.llm_client import get_client, chat


def render():
    st.markdown('<div class="section-header">🤖 Chat Assistant — Ask About Your Contract</div>',
                unsafe_allow_html=True)

    if "state" not in st.session_state or not st.session_state.state:
        st.info("No contract analysed yet. Go to **🏠 Home & Upload** first.")
        return

    s = st.session_state.state

    st.markdown(f"""
    <div class="card card-navy" style="margin-bottom:1rem;">
        <b>💬 Contract Q&A Mode</b><br>
        <span style="color:#AAC8E8;font-size:.85rem;">
            Ask anything about <b>{s.get('filename','')}</b>.
            The assistant knows all clause details, risk counts, scores, and metadata.
        </span>
    </div>""", unsafe_allow_html=True)

    # Suggested questions
    st.markdown("**💡 Suggested questions:**")
    suggestions = [
        "What are the biggest risks in this contract?",
        "How many clauses are HIGH, MEDIUM and LOW risk?",
        "Summarise the payment terms.",
        "Is the liability clause fair?",
        "What should I negotiate before signing?",
        "Explain the termination clause simply.",
        "What IP rights do I get?",
        "What is the governing law?",
    ]
    scols = st.columns(4)
    for i, q in enumerate(suggestions):
        if scols[i % 4].button(q, key=f"sq_{i}", use_container_width=True):
            st.session_state.setdefault("chat_messages", [])
            st.session_state["chat_messages"].append({"role": "user", "content": q})
            _get_response(s, q)
            st.rerun()

    st.markdown("---")

    if "chat_messages" not in st.session_state:
        st.session_state["chat_messages"] = []

    for msg in st.session_state["chat_messages"]:
        role  = msg["role"]
        icon  = "🧑" if role == "user" else "⚖️"
        align = "right" if role == "user" else "left"
        bg    = "#EBF3FB" if role == "user" else "white"
        border= "#2E75B6" if role == "user" else "#2E8B57"
        st.markdown(f"""
        <div style="text-align:{align};margin-bottom:8px;">
            <div style="display:inline-block;background:{bg};border:1px solid {border};
                        border-radius:10px;padding:10px 14px;max-width:80%;
                        font-size:.88rem;line-height:1.6;text-align:left;">
                <b>{icon}</b> {msg['content']}
            </div>
        </div>""", unsafe_allow_html=True)

    user_input = st.chat_input("Ask anything about the contract...")
    if user_input:
        st.session_state["chat_messages"].append({"role": "user", "content": user_input})
        _get_response(s, user_input)
        st.rerun()

    if st.button("🗑️ Clear Chat", key="clear_chat"):
        st.session_state["chat_messages"] = []
        st.rerun()


def _build_context(state: dict) -> str:
    """FIX: build a rich context with ALL risk counts and clause-level detail."""
    cls   = state.get("clauses", [])
    meta  = state.get("extracted_metadata", {})
    score = state.get("risk_score", 0)
    bd    = state.get("risk_breakdown", {})

    # FIX: count all risk levels directly from clauses (not just from breakdown dict)
    high_cls   = [c for c in cls if c.get("risk_level") == "HIGH"]
    medium_cls = [c for c in cls if c.get("risk_level") == "MEDIUM"]
    low_cls    = [c for c in cls if c.get("risk_level") == "LOW"]
    none_cls   = [c for c in cls if c.get("risk_level") == "NONE"]

    # Category-wise breakdown
    from collections import defaultdict
    cat_risk = defaultdict(list)
    for c in cls:
        cat_risk[c.get("category", "General")].append(c.get("risk_level", "NONE"))

    cat_summary = "\n".join(
        f"  - {cat}: {risks.count('HIGH')} HIGH, {risks.count('MEDIUM')} MEDIUM, "
        f"{risks.count('LOW')} LOW, {risks.count('NONE')} OK"
        for cat, risks in sorted(cat_risk.items())
    )

    high_detail = "\n".join(
        f"  [{c['id']}] {c.get('category','')} — {c.get('risk_issue','')} | {c.get('risk_impact','')}"
        for c in high_cls[:8]
    )
    medium_detail = "\n".join(
        f"  [{c['id']}] {c.get('category','')} — {c.get('risk_issue','')}"
        for c in medium_cls[:6]
    )

    parties = meta.get("parties", {})

    return f"""You are LexaGuard AI, a legal contract analyst assistant.
You have fully analysed the contract and have access to all results below.

=== CONTRACT OVERVIEW ===
File: {state.get('filename', '')}
Type: {meta.get('contract_type', 'Unknown')}
Party A: {parties.get('party_a', 'Unknown')}
Party B: {parties.get('party_b', 'Unknown')}
Effective Date: {meta.get('effective_date', 'Unknown')}
Expiry Date: {meta.get('expiry_date', 'Unknown')}
Contract Value: {meta.get('contract_value', 'Unknown')}
Payment Terms: {meta.get('payment_terms', 'Unknown')}
Late Penalty: {meta.get('late_penalty', 'Unknown')}
Termination Notice: {meta.get('termination_notice', 'Unknown')}
Governing Law: {meta.get('governing_law', 'Unknown')}

=== RISK SCORE ===
Overall Score: {score}/100
Financial Risk: {bd.get('financial', 'Unknown')}
Legal Risk: {bd.get('legal', 'Unknown')}
Operational Risk: {bd.get('operational', 'Unknown')}

=== CLAUSE COUNTS ===
Total Clauses: {len(cls)}
HIGH risk:   {len(high_cls)} clauses
MEDIUM risk: {len(medium_cls)} clauses
LOW risk:    {len(low_cls)} clauses
OK (NONE):   {len(none_cls)} clauses

=== CATEGORY-WISE RISK BREAKDOWN ===
{cat_summary}

=== HIGH RISK CLAUSES (detail) ===
{high_detail if high_detail else 'None'}

=== MEDIUM RISK CLAUSES (detail) ===
{medium_detail if medium_detail else 'None'}

=== EXECUTIVE SUMMARY ===
{state.get('executive_summary', '')[:600]}

=== TOP RECOMMENDATIONS ===
{chr(10).join(f'{i+1}. {r}' for i, r in enumerate(state.get('recommendations', [])[:6]))}

Answer the user's question using the data above. Be specific — cite clause IDs and counts.
Always act as a legal assistant, not a lawyer. If asked for category-wise counts, use the
CLAUSE COUNTS and CATEGORY-WISE RISK BREAKDOWN sections above."""


def _get_response(state: dict, question: str):
    history  = st.session_state.get("chat_messages", [])
    context  = _build_context(state)
    messages = [{"role": "system", "content": context}] + \
               [{"role": m["role"], "content": m["content"]} for m in history]

    try:
        client   = get_client()
        response = chat(client, messages, temperature=0.3, max_tokens=800)
    except Exception as e:
        response = f"Error: {e}"

    st.session_state["chat_messages"].append({"role": "assistant", "content": response})