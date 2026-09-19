"""Page: Plain Language Summary"""
import streamlit as st

RISK_ICON  = {"HIGH":"🔴","MEDIUM":"🟡","LOW":"🟢","NONE":"⚪"}
RISK_COLOR = {"HIGH":"#C00000","MEDIUM":"#E07000","LOW":"#2E8B57","NONE":"#888"}
RISK_BG    = {"HIGH":"#FFECEC","MEDIUM":"#FFF4E6","LOW":"#EAFAF2","NONE":"#F8F9FC"}
RISK_BORDER= {"HIGH":"#C00000","MEDIUM":"#E07000","LOW":"#2E8B57","NONE":"#CCCCCC"}

def render():
    st.markdown('<div class="section-header">💬 Plain Language Summary</div>',
                unsafe_allow_html=True)

    if "state" not in st.session_state or not st.session_state.state:
        st.info("No contract analysed yet. Go to **🏠 Home & Upload** first.")
        return

    s    = st.session_state.state
    cls  = s.get("clauses",[])
    meta = s.get("extracted_metadata",{})
    score= s.get("risk_score",0)
    bd   = s.get("risk_breakdown",{})
    color= "#C00000" if score>60 else "#E07000" if score>30 else "#2E8B57"
    verdict = ("High Risk — Do NOT sign without legal review." if score>60 else
               "Medium Risk — Several clauses need negotiation." if score>30 else
               "Low Risk — Minor issues only, review recommended.")

    st.markdown(f"""
    <div class="card card-navy" style="margin-bottom:1.2rem;">
        <div style="display:flex;align-items:center;gap:1.2rem;">
            <div style="font-size:3rem;font-weight:900;color:{color};">{score}</div>
            <div>
                <div style="font-size:1.1rem;font-weight:700;">{verdict}</div>
                <div style="color:#AAC8E8;font-size:.85rem;">
                    {meta.get('contract_type','Unknown')} &nbsp;|&nbsp;
                    {meta.get('parties',{}).get('party_a','?')} ↔ {meta.get('parties',{}).get('party_b','?')}
                </div>
                <div style="color:#AAC8E8;font-size:.8rem;margin-top:4px;">
                    🔴 {bd.get('high_count',0)} High &nbsp;
                    🟡 {bd.get('medium_count',0)} Medium &nbsp;
                    🟢 {bd.get('low_count',0)} Low
                </div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-header">📖 What This Contract Says</div>',
                unsafe_allow_html=True)
    st.markdown(f"""
    <div class="card" style="font-size:.95rem;line-height:1.8;">
        {s.get("plain_summary","Plain summary not available.")}
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-header">📌 Key Facts</div>', unsafe_allow_html=True)
    facts = [
        ("💰","Contract Value",        meta.get("contract_value","Unknown")),
        ("📅","Effective Date",        meta.get("effective_date","Unknown")),
        ("📅","Expiry Date",           meta.get("expiry_date","Unknown")),
        ("💳","Payment Terms",         meta.get("payment_terms","Unknown")),
        ("⚠️","Late Penalty",          meta.get("late_penalty","Unknown")),
        ("🔔","Termination Notice",    meta.get("termination_notice","Unknown")),
        ("🌍","Governing Law",         meta.get("governing_law","Unknown")),
        ("📑","Contract Type",         meta.get("contract_type","Unknown")),
    ]
    cols = st.columns(4)
    for i,(icon,label,val) in enumerate(facts):
        cols[i%4].markdown(f"""
        <div class="metric-box" style="margin-bottom:8px;">
            <div style="font-size:1.3rem;">{icon}</div>
            <div style="font-size:.7rem;color:#666;font-weight:600;">{label}</div>
            <div style="font-size:.82rem;color:#1A2B5E;font-weight:700;">{val}</div>
        </div>""", unsafe_allow_html=True)

    # Obligations
    ob_a = meta.get("key_obligations_party_a",[])
    ob_b = meta.get("key_obligations_party_b",[])
    if ob_a or ob_b:
        st.markdown('<div class="section-header">📋 Key Obligations</div>',
                    unsafe_allow_html=True)
        oc1,oc2 = st.columns(2)
        with oc1:
            st.markdown(f"**{meta.get('parties',{}).get('party_a','Party A')} must:**")
            for o in ob_a[:6]: st.markdown(f"• {o}")
        with oc2:
            st.markdown(f"**{meta.get('parties',{}).get('party_b','Party B')} must:**")
            for o in ob_b[:6]: st.markdown(f"• {o}")

    st.markdown('<div class="section-header">🔍 Every Clause — Simply Explained</div>',
                unsafe_allow_html=True)
    order = {"HIGH":0,"MEDIUM":1,"LOW":2,"NONE":3}
    sorted_cls = sorted(cls, key=lambda c: order.get(c.get("risk_level","NONE"),3))

    for c in sorted_cls:
        risk   = c.get("risk_level","NONE")
        plain  = c.get("plain_english") or c["text"][:120]+"..."
        issue  = c.get("risk_issue","")
        st.markdown(f"""
        <div style="background:{RISK_BG.get(risk,'#F8F9FC')};
                    border-left:4px solid {RISK_BORDER.get(risk,'#CCC')};
                    border-radius:0 8px 8px 0;padding:10px 14px;margin-bottom:7px;">
            <div style="display:flex;justify-content:space-between;margin-bottom:3px;">
                <span style="font-weight:700;font-size:.85rem;color:#1A2B5E;">
                    {RISK_ICON.get(risk,'⚪')} {c['id']} — {c.get('category','?')}
                </span>
                <span class="badge-{risk}">{risk}</span>
            </div>
            <div style="font-size:.88rem;color:#2C2C2C;line-height:1.6;">{plain}</div>
            {f'<div style="font-size:.78rem;color:{RISK_COLOR.get(risk,"#888")};margin-top:4px;">⚠️ {issue}</div>' if issue else ''}
        </div>""", unsafe_allow_html=True)
