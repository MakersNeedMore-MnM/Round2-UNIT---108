"""Page: Redline View"""
import streamlit as st

RISK_COLOR  = {"HIGH":"#C00000","MEDIUM":"#E07000","LOW":"#2E8B57","NONE":"#888"}
RISK_BG     = {"HIGH":"#FFECEC","MEDIUM":"#FFF4E6","LOW":"#EAFAF2","NONE":"#F8F9FC"}

def render():
    st.markdown('<div class="section-header">✏️ Redline View — Suggested Clause Rewrites</div>',
                unsafe_allow_html=True)

    if "state" not in st.session_state or not st.session_state.state:
        st.info("No contract analysed yet. Go to **🏠 Home & Upload** first.")
        return

    cls = st.session_state.state.get("clauses", [])
    risky = [c for c in cls if c.get("risk_level") in ("HIGH","MEDIUM") and c.get("redline_suggestion")]

    if not risky:
        st.success("✅ No high or medium risk clauses requiring redlines found.")
        return

    st.markdown(f"""
    <div class="card card-navy" style="margin-bottom:1rem;">
        <b>⚖️ Redlining Summary</b><br>
        <span style="color:#AAC8E8;font-size:.88rem;">
            {len([c for c in risky if c['risk_level']=='HIGH'])} HIGH-risk and
            {len([c for c in risky if c['risk_level']=='MEDIUM'])} MEDIUM-risk clauses
            have suggested rewrites below. Use these during negotiation.
        </span>
    </div>""", unsafe_allow_html=True)

    # Filter
    risk_filter = st.multiselect("Show risk levels", ["HIGH","MEDIUM"], default=["HIGH","MEDIUM"])
    filtered = [c for c in risky if c.get("risk_level") in risk_filter]

    for c in filtered:
        risk   = c.get("risk_level","MEDIUM")
        color  = RISK_COLOR.get(risk,"#888")
        cat    = c.get("category","?")
        issue  = c.get("risk_issue","")

        with st.expander(f"{'🔴' if risk=='HIGH' else '🟡'} {c['id']} — {cat} | {issue}", expanded=(risk=="HIGH")):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**🔴 Original Clause**")
                st.markdown(f"""
                <div style="background:#FFECEC;border:1px solid {color};border-radius:6px;
                            padding:12px;font-size:.85rem;line-height:1.6;min-height:120px;">
                    {c['text'][:600]}
                </div>""", unsafe_allow_html=True)
                if c.get("risk_impact"):
                    st.markdown(f"""
                    <div style="background:#FFF0F0;border-left:3px solid #C00000;padding:8px;
                                border-radius:0 4px 4px 0;margin-top:6px;font-size:.82rem;">
                        ⚠️ <b>Risk:</b> {c['risk_impact']}
                    </div>""", unsafe_allow_html=True)

            with col2:
                st.markdown("**🟢 Suggested Redline**")
                st.markdown(f"""
                <div style="background:#EAFAF2;border:1px solid #2E8B57;border-radius:6px;
                            padding:12px;font-size:.85rem;line-height:1.6;min-height:120px;">
                    {c.get('redline_suggestion','')}
                </div>""", unsafe_allow_html=True)
                if c.get("negotiation_tip"):
                    st.markdown(f"""
                    <div style="background:#FFF4E6;border-left:3px solid #E07000;padding:8px;
                                border-radius:0 4px 4px 0;margin-top:6px;font-size:.82rem;">
                        💡 <b>Negotiation Tip:</b> {c['negotiation_tip']}
                    </div>""", unsafe_allow_html=True)

            if c.get("legal_reasoning"):
                st.markdown("**⚖️ Legal Reasoning**")
                st.markdown(f"""
                <div class="card" style="font-size:.84rem;margin-top:4px;">
                    {c['legal_reasoning']}
                </div>""", unsafe_allow_html=True)
