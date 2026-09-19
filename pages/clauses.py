"""Page: Clause Browser with side-by-side diff view"""
import streamlit as st
from data.templates import STANDARD_TEMPLATES


RISK_EMOJI = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢", "NONE": "⚪"}
RISK_COLOR = {"HIGH": "#C00000", "MEDIUM": "#E07000", "LOW": "#2E8B57", "NONE": "#888"}


def render():
    st.markdown('<div class="section-header">📋 Clause Browser</div>', unsafe_allow_html=True)

    if "state" not in st.session_state or not st.session_state.state:
        st.info("No contract analysed yet. Go to **🏠 Home & Upload** to upload a contract.")
        return

    cls = st.session_state.state.get("clauses", [])
    if not cls:
        st.warning("No clauses found.")
        return

    # ── Filters ───────────────────────────────────────────────────────────────
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        risk_filter = st.multiselect(
            "Filter by Risk", ["HIGH", "MEDIUM", "LOW", "NONE"],
            default=["HIGH", "MEDIUM", "LOW", "NONE"],
        )
    with col2:
        cats = sorted(set(c.get("category","?") for c in cls))
        cat_filter = st.multiselect("Filter by Category", cats, default=cats)
    with col3:
        search = st.text_input("🔍 Search clause text", placeholder="keyword...")

    # Apply filters
    filtered = [
        c for c in cls
        if c.get("risk_level","NONE") in risk_filter
        and c.get("category","?") in cat_filter
        and (not search or search.lower() in c["text"].lower())
    ]

    st.markdown(f"**Showing {len(filtered)} of {len(cls)} clauses**")
    st.markdown("---")

    if not filtered:
        st.info("No clauses match your filters.")
        return

    # Sort: HIGH first
    order = {"HIGH":0,"MEDIUM":1,"LOW":2,"NONE":3}
    filtered = sorted(filtered, key=lambda c: order.get(c.get("risk_level","NONE"),3))

    for clause in filtered:
        _render_clause_card(clause)


def _render_clause_card(c: dict):
    risk  = c.get("risk_level","NONE")
    cat   = c.get("category","?")
    issue = c.get("risk_issue","")
    emoji = RISK_EMOJI.get(risk,"⚪")
    color = RISK_COLOR.get(risk,"#888")

    header = f"{emoji} **{c['id']}** — {cat} &nbsp; <span class='badge-{risk}'>{risk}</span>"
    if issue:
        header += f" &nbsp;|&nbsp; <span style='color:{color};font-size:0.82rem;'>{issue}</span>"

    with st.expander(f"{emoji} {c['id']} — {cat} [{risk}]{' | ' + issue if issue else ''}", expanded=(risk=="HIGH")):
        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            ["📄 Original", "📊 Template Diff", "⚖️ Legal Analysis", "💬 Plain English", "✏️ Redline"]
        )

        with tab1:
            st.markdown(f"""
            <div style="background:#F8F9FC;border-radius:6px;padding:12px;font-size:0.88rem;line-height:1.6;border:1px solid #dde5f0;">
                {c['text']}
            </div>""", unsafe_allow_html=True)
            if c.get("confidence"):
                st.caption(f"Classification confidence: {c['confidence']:.0%}")

        with tab2:
            std_template = STANDARD_TEMPLATES.get(cat, {})
            std_text     = std_template.get("standard","No standard template for this category.")
            dev_score    = c.get("deviation_score", 0)
            deviation    = c.get("template_deviation","")

            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("**📘 Standard Template**")
                st.markdown(f"""<div style="background:#EBF3FB;border-radius:6px;padding:10px;font-size:0.83rem;line-height:1.5;border:1px solid #2E75B6;">{std_text}</div>""", unsafe_allow_html=True)
                if std_template.get("key_elements"):
                    st.markdown("**Must-have elements:**")
                    for el in std_template["key_elements"]:
                        st.markdown(f"✅ {el}")
            with col_b:
                st.markdown("**📄 Your Contract Clause**")
                st.markdown(f"""<div style="background:#{'FFECEC' if dev_score>0.6 else 'FFF4E6' if dev_score>0.3 else 'EAFAF2'};border-radius:6px;padding:10px;font-size:0.83rem;line-height:1.5;border:1px solid {RISK_COLOR.get(risk,'#888')};">{c['text'][:600]}</div>""", unsafe_allow_html=True)
                if std_template.get("red_flags"):
                    st.markdown("**Watch for:**")
                    for rf in std_template["red_flags"]:
                        found = any(w in c["text"].lower() for w in rf.lower().split()[:2])
                        icon  = "🚨" if found else "✅"
                        st.markdown(f"{icon} {rf}")

            st.markdown(f"**Deviation Score:** `{dev_score:.0%}`")
            if deviation:
                st.info(f"📊 {deviation}")

        with tab3:
            if c.get("risk_impact"):
                st.markdown(f"""<div style="background:#FFECEC;border-left:4px solid #C00000;padding:10px;border-radius:0 6px 6px 0;margin-bottom:8px;">
                    <b>Impact:</b> {c['risk_impact']}</div>""", unsafe_allow_html=True)
            if c.get("legal_reasoning"):
                st.markdown(f"""<div class="card">{c['legal_reasoning']}</div>""", unsafe_allow_html=True)
            else:
                st.info("Legal reasoning not available for this clause (LOW / NONE risk).")

        with tab4:
            if c.get("plain_english"):
                st.markdown(f"""
                <div style="background:#EBF3FB;border-radius:8px;padding:14px;font-size:0.92rem;line-height:1.7;border:1px solid #2E75B6;">
                    💬 {c['plain_english']}
                </div>""", unsafe_allow_html=True)
            else:
                st.info("Plain English translation not available.")

        with tab5:
            if c.get("redline_suggestion"):
                st.markdown("**🔴 Suggested Redline (safer wording):**")
                st.markdown(f"""<div style="background:#EAFAF2;border-left:4px solid #2E8B57;padding:12px;border-radius:0 6px 6px 0;font-size:0.88rem;line-height:1.6;">{c['redline_suggestion']}</div>""", unsafe_allow_html=True)
            if c.get("negotiation_tip"):
                st.markdown("**💡 Negotiation Tip:**")
                st.markdown(f"""<div style="background:#FFF4E6;border-left:4px solid #E07000;padding:10px;border-radius:0 6px 6px 0;font-size:0.85rem;">{c['negotiation_tip']}</div>""", unsafe_allow_html=True)
            if not c.get("redline_suggestion") and not c.get("negotiation_tip"):
                st.success("✅ This clause does not require redlining.")
