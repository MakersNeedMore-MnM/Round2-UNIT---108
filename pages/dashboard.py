"""Page: Risk Dashboard"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


def render():
    st.markdown('<div class="section-header">📊 Risk Dashboard</div>', unsafe_allow_html=True)

    if "state" not in st.session_state or not st.session_state.state:
        st.info("No contract analysed yet. Go to **🏠 Home & Upload** to upload a contract.")
        return

    s      = st.session_state.state
    score  = s.get("risk_score", 0)
    bd     = s.get("risk_breakdown", {})
    cls    = s.get("clauses", [])
    meta   = s.get("extracted_metadata", {})

    color = "#C00000" if score > 60 else "#E07000" if score > 30 else "#2E8B57"
    label = "HIGH RISK" if score > 60 else "MEDIUM RISK" if score > 30 else "LOW RISK"

    # ── Top KPIs ──────────────────────────────────────────────────────────────
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.markdown(f"""<div class="metric-box"><div class="val" style="color:{color};">{score}</div><div class="lbl">Overall Risk Score</div></div>""", unsafe_allow_html=True)
    k2.markdown(f"""<div class="metric-box"><div class="val" style="color:#C00000;">{bd.get('high_count',0)}</div><div class="lbl">🔴 High Risk</div></div>""", unsafe_allow_html=True)
    k3.markdown(f"""<div class="metric-box"><div class="val" style="color:#E07000;">{bd.get('medium_count',0)}</div><div class="lbl">🟡 Medium Risk</div></div>""", unsafe_allow_html=True)
    k4.markdown(f"""<div class="metric-box"><div class="val" style="color:#2E8B57;">{bd.get('low_count',0)}</div><div class="lbl">🟢 Low Risk</div></div>""", unsafe_allow_html=True)
    k5.markdown(f"""<div class="metric-box"><div class="val" style="color:#1A2B5E;">{len(cls)}</div><div class="lbl">Total Clauses</div></div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Row 1: Gauge + Dimension bars + Donut ─────────────────────────────────
    c1, c2, c3 = st.columns([1, 1.2, 1])

    with c1:
        st.markdown("**Overall Risk Gauge**")
        gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=score,
            title={"text": label, "font": {"size": 13, "color": color}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#666"},
                "bar": {"color": color},
                "steps": [
                    {"range": [0, 30],  "color": "#EAFAF2"},
                    {"range": [30, 60], "color": "#FFF4E6"},
                    {"range": [60, 100],"color": "#FFECEC"},
                ],
                "threshold": {"line": {"color": "#1A2B5E", "width": 3}, "thickness": 0.8, "value": score},
            },
            number={"suffix": "/100", "font": {"size": 28, "color": color}},
        ))
        gauge.update_layout(height=240, margin=dict(t=30, b=10, l=20, r=20), paper_bgcolor="white")
        st.plotly_chart(gauge, use_container_width=True)

    with c2:
        st.markdown("**Risk Dimensions**")
        dim_map = {"High": 80, "Medium": 45, "Low": 15}
        dims = {
            "Financial": dim_map.get(bd.get("financial","Low"), 15),
            "Legal": dim_map.get(bd.get("legal","Low"), 15),
            "Operational": dim_map.get(bd.get("operational","Low"), 15),
        }
        dim_colors = ["#C00000" if v >= 60 else "#E07000" if v >= 30 else "#2E8B57" for v in dims.values()]
        bar = go.Figure(go.Bar(
            x=list(dims.values()), y=list(dims.keys()),
            orientation="h",
            marker_color=dim_colors,
            text=[f"{v}/100" for v in dims.values()],
            textposition="outside",
        ))
        bar.update_layout(
            height=240, margin=dict(t=10, b=10, l=10, r=40),
            xaxis=dict(range=[0, 110], showgrid=False, zeroline=False),
            yaxis=dict(tickfont=dict(size=12)),
            paper_bgcolor="white", plot_bgcolor="white",
        )
        st.plotly_chart(bar, use_container_width=True)

    with c3:
        st.markdown("**Clause Risk Distribution**")
        high   = bd.get("high_count", 0)
        medium = bd.get("medium_count", 0)
        low    = bd.get("low_count", 0)
        none_c = len(cls) - high - medium - low
        donut = go.Figure(go.Pie(
            labels=["High", "Medium", "Low", "None"],
            values=[high, medium, low, max(none_c, 0)],
            hole=0.55,
            marker_colors=["#C00000", "#E07000", "#2E8B57", "#CCCCCC"],
            textfont_size=11,
        ))
        donut.update_layout(
            height=240, margin=dict(t=10, b=10, l=10, r=10),
            legend=dict(orientation="h", y=-0.15, font_size=10),
            paper_bgcolor="white",
        )
        st.plotly_chart(donut, use_container_width=True)

    st.markdown("---")

    # ── Row 2: Category heatmap + Deviation scatter ───────────────────────────
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("**Risk by Clause Category**")
        if cls:
            df = pd.DataFrame([
                {"Category": c.get("category","?"), "Risk": c.get("risk_level","NONE"), "Score": c.get("deviation_score",0)}
                for c in cls
            ])
            cat_risk = df.groupby("Category")["Score"].mean().reset_index()
            cat_risk = cat_risk.sort_values("Score", ascending=True)
            colors_ = ["#C00000" if v > 0.6 else "#E07000" if v > 0.3 else "#2E8B57" for v in cat_risk["Score"]]
            fig = go.Figure(go.Bar(
                x=cat_risk["Score"].round(2),
                y=cat_risk["Category"],
                orientation="h",
                marker_color=colors_,
                text=[f"{v:.0%}" for v in cat_risk["Score"]],
                textposition="outside",
            ))
            fig.update_layout(
                height=300, margin=dict(t=10, b=10, l=10, r=50),
                xaxis=dict(range=[0,1.2], tickformat=".0%", showgrid=False),
                paper_bgcolor="white", plot_bgcolor="white",
            )
            st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("**Deviation Score per Clause**")
        if cls:
            df2 = pd.DataFrame([
                {
                    "Clause": c["id"],
                    "Deviation": round(c.get("deviation_score", 0), 2),
                    "Risk":      c.get("risk_level","NONE"),
                    "Category":  c.get("category","?"),
                }
                for c in cls
            ])
            color_map = {"HIGH":"#C00000","MEDIUM":"#E07000","LOW":"#2E8B57","NONE":"#CCCCCC"}
            scatter = px.scatter(
                df2, x="Clause", y="Deviation", color="Risk",
                color_discrete_map=color_map,
                hover_data=["Category"],
                size=[10]*len(df2),
            )
            scatter.update_layout(
                height=300, margin=dict(t=10, b=10, l=10, r=10),
                yaxis=dict(range=[0,1.1], title="Deviation Score"),
                legend=dict(orientation="h", y=-0.25, font_size=10),
                paper_bgcolor="white", plot_bgcolor="#F8F9FC",
            )
            st.plotly_chart(scatter, use_container_width=True)

    st.markdown("---")

    # ── Contract metadata table ───────────────────────────────────────────────
    st.markdown("**Contract Key Information**")
    parties = meta.get("parties", {})
    info = {
        "Contract Type":    meta.get("contract_type","Unknown"),
        "Party A":          parties.get("party_a","Unknown"),
        "Party B":          parties.get("party_b","Unknown"),
        "Effective Date":   meta.get("effective_date","Unknown"),
        "Expiry Date":      meta.get("expiry_date","Unknown"),
        "Contract Value":   meta.get("contract_value","Unknown"),
        "Payment Terms":    meta.get("payment_terms","Unknown"),
        "Late Penalty":     meta.get("late_penalty","Unknown"),
        "Termination Notice": meta.get("termination_notice","Unknown"),
        "Governing Law":    meta.get("governing_law","Unknown"),
    }
    df_meta = pd.DataFrame(list(info.items()), columns=["Field","Value"])
    st.dataframe(df_meta, use_container_width=True, hide_index=True)

    # ── Executive summary ─────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("**Executive Summary**")
    st.markdown(f"""<div class="card">{s.get("executive_summary","")}</div>""", unsafe_allow_html=True)

    # ── Recommendations ───────────────────────────────────────────────────────
    st.markdown("**Recommendations**")
    for i, rec in enumerate(s.get("recommendations", []), 1):
        st.markdown(f"""
        <div style="background:white;border-left:3px solid #2E75B6;padding:8px 12px;margin-bottom:6px;border-radius:0 6px 6px 0;font-size:0.88rem;">
            <b style="color:#1A2B5E;">#{i}</b> {rec}
        </div>""", unsafe_allow_html=True)
