"""Page: Export Reports"""
import streamlit as st
import json
from datetime import datetime
from agents.agent10_report import generate_pdf, generate_docx, generate_json


def render():
    st.markdown('<div class="section-header">📄 Export Reports</div>', unsafe_allow_html=True)

    if "state" not in st.session_state or not st.session_state.state:
        st.info("No contract analysed yet. Go to **🏠 Home & Upload** first.")
        return

    s     = st.session_state.state
    score = s.get("risk_score", 0)
    fname = s.get("filename","contract").rsplit(".",1)[0]
    stamp = datetime.now().strftime("%Y%m%d_%H%M")

    color = "#C00000" if score > 60 else "#E07000" if score > 30 else "#2E8B57"
    label = "HIGH RISK" if score > 60 else "MEDIUM RISK" if score > 30 else "LOW RISK"
    bd    = s.get("risk_breakdown", {})

    st.markdown(f"""
    <div class="card card-navy" style="margin-bottom:1.2rem;">
        <div style="display:flex;align-items:center;gap:1.5rem;">
            <div style="font-size:3rem;font-weight:900;color:{color};">{score}</div>
            <div>
                <div style="font-size:1.1rem;font-weight:700;">{label} — {fname}</div>
                <div style="color:#AAC8E8;font-size:.85rem;">
                    {len(s.get('clauses',[]))} clauses &nbsp;|&nbsp;
                    🔴 {bd.get('high_count',0)} High &nbsp;
                    🟡 {bd.get('medium_count',0)} Medium &nbsp;
                    🟢 {bd.get('low_count',0)} Low
                </div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("""
        <div class="card" style="text-align:center;min-height:160px;">
            <div style="font-size:2.5rem;">📕</div>
            <div style="font-weight:700;color:#1A2B5E;margin:6px 0;">PDF Report</div>
            <div style="font-size:.8rem;color:#666;">Full structured report with risk matrix,
            clause breakdown, recommendations & plain summary.</div>
        </div>""", unsafe_allow_html=True)
        if st.button("⬇️ Download PDF", use_container_width=True, key="pdf"):
            with st.spinner("Generating PDF..."):
                try:
                    pdf_bytes = generate_pdf(s)
                    st.download_button("📥 Save PDF", pdf_bytes,
                        file_name=f"LexaGuard_{fname}_{stamp}.pdf",
                        mime="application/pdf", use_container_width=True)
                except Exception as e:
                    st.error(f"PDF error: {e}")

    with c2:
        st.markdown("""
        <div class="card" style="text-align:center;min-height:160px;">
            <div style="font-size:2.5rem;">📘</div>
            <div style="font-weight:700;color:#1A2B5E;margin:6px 0;">Word Report</div>
            <div style="font-size:.8rem;color:#666;">DOCX with tracked redline suggestions,
            legal analysis, and full clause commentary.</div>
        </div>""", unsafe_allow_html=True)
        if st.button("⬇️ Download DOCX", use_container_width=True, key="docx"):
            with st.spinner("Generating DOCX..."):
                try:
                    docx_bytes = generate_docx(s)
                    st.download_button("📥 Save DOCX", docx_bytes,
                        file_name=f"LexaGuard_{fname}_{stamp}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True)
                except Exception as e:
                    st.error(f"DOCX error: {e}")

    with c3:
        st.markdown("""
        <div class="card" style="text-align:center;min-height:160px;">
            <div style="font-size:2.5rem;">📗</div>
            <div style="font-weight:700;color:#1A2B5E;margin:6px 0;">JSON Export</div>
            <div style="font-size:.8rem;color:#666;">Machine-readable structured data.
            All clauses, risk scores, metadata — ideal for API integration.</div>
        </div>""", unsafe_allow_html=True)
        if st.button("⬇️ Download JSON", use_container_width=True, key="json"):
            with st.spinner("Generating JSON..."):
                try:
                    json_str = generate_json(s)
                    st.download_button("📥 Save JSON", json_str,
                        file_name=f"LexaGuard_{fname}_{stamp}.json",
                        mime="application/json", use_container_width=True)
                except Exception as e:
                    st.error(f"JSON error: {e}")

    # Report preview
    st.markdown("---")
    st.markdown('<div class="section-header">👁️ Report Preview</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📋 Executive Summary", "⚠️ High Risk Clauses", "✅ Recommendations"])

    with tab1:
        st.markdown(f'<div class="card" style="font-size:.92rem;line-height:1.8;">{s.get("executive_summary","")}</div>',
                    unsafe_allow_html=True)

    with tab2:
        high_cls = [c for c in s.get("clauses",[]) if c.get("risk_level")=="HIGH"]
        if not high_cls:
            st.success("No HIGH risk clauses found.")
        for c in high_cls:
            st.markdown(f"""
            <div style="background:#FFECEC;border-left:4px solid #C00000;padding:10px 14px;
                        border-radius:0 8px 8px 0;margin-bottom:8px;">
                <b style="color:#C00000;">{c['id']} — {c.get('category','')}
                &nbsp;|&nbsp; {c.get('risk_issue','')}</b><br>
                <span style="font-size:.85rem;">{c['text'][:300]}...</span><br>
                {f"<span style='font-size:.82rem;color:#2E8B57;'><b>Redline:</b> {c['redline_suggestion'][:200]}</span>" if c.get('redline_suggestion') else ''}
            </div>""", unsafe_allow_html=True)

    with tab3:
        for i, rec in enumerate(s.get("recommendations",[]), 1):
            st.markdown(f"""
            <div style="background:white;border-left:3px solid #2E75B6;padding:8px 12px;
                        margin-bottom:6px;border-radius:0 6px 6px 0;font-size:.88rem;">
                <b style="color:#1A2B5E;">#{i}</b> {rec}
            </div>""", unsafe_allow_html=True)
