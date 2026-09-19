"""Page: Home & Upload"""
import streamlit as st
import time
from orchestrator import run_pipeline


def render():
    st.markdown('<div class="section-header">🏠 LexaGuard AI — Legal Contract Intelligence</div>',
                unsafe_allow_html=True)

    st.markdown("""
    <div class="card card-navy" style="margin-bottom:1.5rem;">
        <h2 style="margin:0;font-size:1.6rem;">⚖️ LexaGuard AI</h2>
        <p style="margin:6px 0 0 0;color:#AAC8E8;font-size:.95rem;">
            Autonomous Multi agent legal contract analysis powered by Gemini.
            Upload any contract and get a full risk assessment in minutes.
        </p>
    </div>""", unsafe_allow_html=True)

    cols = st.columns(5)
    for col, (icon, label) in zip(cols, [
        ("🔍","Clause Extraction"), ("⚠️","Risk Detection"),
        ("📊","RAG Comparison"),    ("💬","Plain English"), ("✏️","Auto Redlines"),
    ]):
        col.markdown(f"""<div class="metric-box"><div style="font-size:1.4rem;">{icon}</div>
            <div style="font-size:.75rem;color:#1A2B5E;font-weight:600;">{label}</div></div>""",
            unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-header">📁 Upload Contract</div>', unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Drop your contract here (PDF, DOCX, or TXT)",
        type=["pdf", "docx", "txt"],
    )

    c1, c2 = st.columns([3, 1])
    with c1:
        if uploaded:
            st.success(f"✅ **{uploaded.name}** ({uploaded.size/1024:.1f} KB)")
    with c2:
        if st.button("📄 Use Sample Contract", use_container_width=True):
            _store_sample()
            st.rerun()

    # Resolve bytes + name (uploaded OR sample)
    file_bytes, filename = None, None
    if uploaded:
        file_bytes = uploaded.read()
        filename   = uploaded.name
    elif st.session_state.get("sample_bytes"):
        file_bytes = st.session_state["sample_bytes"]
        filename   = st.session_state["sample_name"]
        st.info(f"Using sample contract: **{filename}**")

    if file_bytes:
        if st.button("🚀 Analyse Contract", type="primary", use_container_width=True):
            _run_analysis(file_bytes, filename)

    if "state" in st.session_state and st.session_state.state:
        _show_preview()


def _run_analysis(file_bytes: bytes, filename: str):
    st.markdown("---")
    st.markdown('<div class="section-header">🔄 Running Multi-Agent Pipeline</div>',
                unsafe_allow_html=True)

    pbar        = st.progress(0)
    status_txt  = st.empty()
    agent_txt   = st.empty()
    step_cols   = st.columns(10)
    indicators  = [col.empty() for col in step_cols]

    try:
        final_state = None
        for update in run_pipeline(file_bytes, filename):
            pct   = update["pct"]
            step  = update["step"]
            pbar.progress(pct / 100)
            status_txt.markdown(f"**{update['label']}**")
            agent_txt.markdown(
                f"<div style='color:#2E75B6;font-size:.8rem;'>Active Agent: {update['agent']}</div>",
                unsafe_allow_html=True)
            for i in range(10):
                if i + 1 < step:
                    indicators[i].markdown("✅")
                elif i + 1 == step:
                    indicators[i].markdown("⚙️")
                else:
                    indicators[i].markdown("⬜")
            if update.get("state"):
                final_state = update["state"]

        if final_state and not final_state.get("error"):
            st.session_state.state = final_state
            st.session_state.pop("sample_bytes", None)
            for ind in indicators: ind.markdown("✅")
            pbar.progress(1.0)
            status_txt.markdown("**✅ Analysis complete!**")
            st.success(
                f"🎉 Done! Risk Score: **{final_state['risk_score']}/100** "
                f"| {len(final_state['clauses'])} clauses analysed."
            )
            time.sleep(0.8)
            st.rerun()
        elif final_state and final_state.get("error"):
            st.error(f"❌ {final_state['error'][:600]}")
    except Exception as e:
        st.error(f"❌ {e}")


def _store_sample():
    sample = """VENDOR SERVICE AGREEMENT

This Vendor Service Agreement ("Agreement") is entered into as of January 1, 2025,
between TechCorp Solutions Pvt. Ltd. ("Vendor") and GlobalMart Enterprises Ltd. ("Client").

1. SERVICES
1.1 The Vendor shall provide software development and maintenance services.
1.2 Services commence February 1, 2025 and continue until terminated.

2. PAYMENT TERMS
2.1 Client shall pay INR 5,00,000 per month for services rendered.
2.2 Payment within 60 days of invoice. Late payments accrue interest at 3% per month compounded monthly.
2.3 Vendor may suspend services without notice if payment is overdue by more than 30 days.

3. INTELLECTUAL PROPERTY
3.1 All IP including code, designs, and documentation created under this Agreement shall remain
    the exclusive property of the Vendor.
3.2 Client is granted a non-exclusive, non-transferable license for internal use only.
3.3 Client shall not reverse engineer or create derivative works from any Vendor IP.

4. LIABILITY
4.1 The Vendor shall not be liable for any damages arising out of this Agreement.
4.2 Client agrees to indemnify and hold harmless the Vendor from any and all claims of any nature.
4.3 There shall be no cap on damages that either party may claim.

5. CONFIDENTIALITY
5.1 Client agrees to maintain confidentiality of all Vendor information indefinitely.
5.2 Vendor has no obligation to maintain confidentiality of any Client information.

6. TERMINATION
6.1 Vendor may terminate this Agreement at any time without notice and without cause.
6.2 Client may only terminate with 90 days written notice plus a termination fee of 6 months fees.
6.3 Upon termination, all licenses granted to Client are immediately revoked.

7. GOVERNING LAW
7.1 This Agreement is governed by the laws of the State of Delaware, USA.
7.2 Disputes resolved exclusively in Delaware courts. Client waives objection to jurisdiction.
7.3 Prevailing party entitled to recover all legal fees from non-prevailing party.

8. FORCE MAJEURE
8.1 Neither party shall be liable for delays caused by circumstances beyond reasonable control.

9. WARRANTIES
9.1 THE VENDOR MAKES NO WARRANTIES, EXPRESS OR IMPLIED.
9.2 Vendor does not warrant that services will be uninterrupted or error-free.

10. ENTIRE AGREEMENT
10.1 This Agreement constitutes the entire agreement between the parties."""

    st.session_state["sample_bytes"] = sample.encode("utf-8")
    st.session_state["sample_name"]  = "Sample_Vendor_Agreement.txt"


def _show_preview():
    s     = st.session_state.state
    score = s.get("risk_score", 0)
    bd    = s.get("risk_breakdown", {})
    color = "#C00000" if score > 60 else "#E07000" if score > 30 else "#2E8B57"
    st.markdown("---")
    st.markdown('<div class="section-header">📊 Results Preview</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="metric-box"><div class="val" style="color:{color};">{score}</div><div class="lbl">Risk Score /100</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="metric-box"><div class="val" style="color:#C00000;">{bd.get("high_count",0)}</div><div class="lbl">🔴 High Risk</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="metric-box"><div class="val" style="color:#E07000;">{bd.get("medium_count",0)}</div><div class="lbl">🟡 Medium Risk</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="metric-box"><div class="val" style="color:#1A2B5E;">{len(s.get("clauses",[]))}</div><div class="lbl">Total Clauses</div></div>', unsafe_allow_html=True)
    st.info("👈 Use the sidebar to explore Risk Dashboard, Clause Browser, and more.")
