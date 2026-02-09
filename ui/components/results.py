"""Results display component — detailed agent findings."""

import streamlit as st
from core.models import AgentResult


_EMOJI_MAP = {
    "Content Quality": "📝",
    "Visual Quality": "🎨",
    "User Experience": "🧭",
    "Trust & Credibility": "🛡️",
    "Technical Health": "⚙️",
}


def _score_color(score: float) -> str:
    if score >= 80:
        return "#22c55e"   # green
    elif score >= 60:
        return "#eab308"   # yellow
    elif score >= 40:
        return "#f97316"   # orange
    else:
        return "#ef4444"   # red


def render_results(results: dict[str, AgentResult]):
    """Render expandable sections for each agent's findings."""
    st.subheader("📋 Detailed Findings")

    for key in ["text", "visual", "ux", "trust", "tech"]:
        result = results[key]
        emoji = _EMOJI_MAP.get(result.agent_name, "📊")
        color = _score_color(result.score)

        with st.expander(
            f"{emoji}  **{result.agent_name}** — Score: {result.score:.0f}/100",
            expanded=False,
        ):
            st.markdown(
                f'<span style="color:{color}; font-size:1.6rem; font-weight:700;">'
                f"{result.score:.0f}/100</span>",
                unsafe_allow_html=True,
            )

            if result.summary:
                st.info(result.summary)

            if result.findings:
                for finding in result.findings:
                    st.markdown(f"- {finding}")
            else:
                st.write("No specific findings.")
