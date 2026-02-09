"""Charts component — radar chart and score overview."""

import streamlit as st
import plotly.graph_objects as go
from core.models import AgentResult


def _grade_color(grade: str) -> str:
    mapping = {"A+": "#16a34a", "A": "#22c55e", "B": "#84cc16",
               "C": "#eab308", "D": "#f97316", "F": "#ef4444"}
    return mapping.get(grade, "#6b7280")


def render_charts(overall: float, grade: str, results: dict[str, AgentResult]):
    """Render the overall score banner and radar chart."""

    # ── Overall score row ───────────────────────────────────────────
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        color = _grade_color(grade)
        st.markdown(
            f"""
            <div style="text-align:center; padding:1rem 0;">
                <div class="score-big" style="color:{color};">{overall:.0f}</div>
                <span class="grade-badge" style="background:{color};">Grade {grade}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── Radar chart ─────────────────────────────────────────────────
    categories = ["Content", "Visual", "UX", "Trust", "Tech"]
    keys = ["text", "visual", "ux", "trust", "tech"]
    values = [results[k].score for k in keys]
    # Close the polygon
    values_closed = values + [values[0]]
    cats_closed = categories + [categories[0]]

    fig = go.Figure(
        data=[
            go.Scatterpolar(
                r=values_closed,
                theta=cats_closed,
                fill="toself",
                fillcolor="rgba(99,102,241,0.25)",
                line=dict(color="#6366f1", width=2),
                name="CEPS",
            )
        ],
        layout=go.Layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=10)),
            ),
            showlegend=False,
            margin=dict(l=60, r=60, t=40, b=40),
            height=370,
        ),
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Quick metrics row ───────────────────────────────────────────
    cols = st.columns(5)
    emojis = ["📝", "🎨", "🧭", "🛡️", "⚙️"]
    for i, (cat, key) in enumerate(zip(categories, keys)):
        with cols[i]:
            st.metric(
                label=f"{emojis[i]} {cat}",
                value=f"{results[key].score:.0f}",
            )
