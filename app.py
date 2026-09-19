"""
LexaGuard AI — Main Application

"""
import streamlit as st

st.set_page_config(
    page_title="LexaGuard AI",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Hide the auto-generated pages nav
st.markdown("<style>[data-testid='stSidebarNavItems']{display:none!important;}[data-testid='stSidebarNavSeparator']{display:none!important;}</style>", unsafe_allow_html=True)

st.markdown("""
<style>
:root{--navy:#1A2B5E;--blue:#2E75B6;--red:#C00000;--amber:#E07000;--green:#2E8B57;--light:#EBF3FB;}
[data-testid="stAppViewContainer"]{background:#F8F9FC;}
[data-testid="stSidebar"]{background:#1A2B5E!important;}
[data-testid="stSidebar"] *{color:white!important;}
.card{background:white;border-radius:10px;padding:1.2rem 1.4rem;margin-bottom:1rem;
      border:1px solid #dde5f0;box-shadow:0 2px 8px rgba(30,60,120,.07);}
.card-navy{background:#1A2B5E;color:white;}
.card-navy *{color:white!important;}
.badge-HIGH{background:#FFECEC;color:#C00000;border:1px solid #C00000;border-radius:4px;padding:2px 8px;font-weight:bold;font-size:12px;}
.badge-MEDIUM{background:#FFF4E6;color:#E07000;border:1px solid #E07000;border-radius:4px;padding:2px 8px;font-weight:bold;font-size:12px;}
.badge-LOW{background:#EAFAF2;color:#2E8B57;border:1px solid #2E8B57;border-radius:4px;padding:2px 8px;font-weight:bold;font-size:12px;}
.badge-NONE{background:#F4F4F4;color:#888;border:1px solid #CCC;border-radius:4px;padding:2px 8px;font-weight:bold;font-size:12px;}
.section-header{font-size:1.1rem;font-weight:700;color:#1A2B5E;border-left:4px solid #2E75B6;
                padding-left:10px;margin:1rem 0 .5rem 0;}
.metric-box{background:white;border-radius:8px;padding:.8rem;text-align:center;border:1px solid #dde5f0;}
.metric-box .val{font-size:1.8rem;font-weight:800;}
.metric-box .lbl{font-size:.75rem;color:#666;}
.clause-card{border-left:4px solid #2E75B6;background:white;border-radius:0 8px 8px 0;
             padding:.8rem 1rem;margin-bottom:.6rem;box-shadow:0 1px 4px rgba(0,0,0,.06);}
</style>
""", unsafe_allow_html=True)

# ── Sidebar nav only — no API key input ──────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚖️ LexaGuard AI")
    st.markdown("**Legal Contract Intelligence**")
    st.markdown("---")
    st.markdown("### Navigation")
    page = st.radio("Navigation", [
        "🏠 Home & Upload",
        "📊 Risk Dashboard",
        "📋 Clause Browser",
        "💬 Plain Summary",
        "✏️  Redline View",
        "📄 Export Reports",
        "🤖 Chat Assistant",
    ], label_visibility="collapsed")

    st.markdown("---")
    if "state" in st.session_state and st.session_state.state:
        s     = st.session_state.state
        score = s.get("risk_score", 0)
        bd    = s.get("risk_breakdown", {})
        color = "#C00000" if score > 60 else "#E07000" if score > 30 else "#2E8B57"
        st.markdown(f"""
        <div style='background:rgba(255,255,255,.1);border-radius:8px;padding:10px;margin-bottom:8px;'>
            <div style='font-size:.75rem;color:#AAC8E8;'>Current Contract</div>
            <div style='font-size:.85rem;font-weight:600;'>{s.get('filename','')[:28]}</div>
            <div style='font-size:2rem;font-weight:900;color:{color};'>{score}
                <span style='font-size:1rem;'>/100</span></div>
            <div style='font-size:.7rem;color:#AAC8E8;'>Risk Score</div>
            <div style='font-size:.72rem;color:#AAC8E8;margin-top:4px;'>
                💰 {bd.get("financial","—")} &nbsp;⚖️ {bd.get("legal","—")} &nbsp;⚙️ {bd.get("operational","—")}
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div style="color:#AAC8E8;font-size:.8rem;">No contract loaded yet.</div>',
                    unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div style="color:#AAC8E8;font-size:.7rem;"></div>',
                unsafe_allow_html=True)

# ── Route ─────────────────────────────────────────────────────────────────────
if   page == "🏠 Home & Upload":   from pages.home      import render; render()
elif page == "📊 Risk Dashboard":  from pages.dashboard import render; render()
elif page == "📋 Clause Browser":  from pages.clauses   import render; render()
elif page == "💬 Plain Summary":   from pages.summary   import render; render()
elif page == "✏️  Redline View":   from pages.redline   import render; render()
elif page == "📄 Export Reports":  from pages.exports   import render; render()
elif page == "🤖 Chat Assistant":  from pages.chat      import render; render()
