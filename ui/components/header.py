"""Header component for the Streamlit UI."""

import streamlit as st


def render_header():
    """Render the app header and description."""
    st.set_page_config(
        page_title="CEPS Analyzer",
        page_icon="🔍",
        layout="wide",
    )

    # Minimal custom CSS
    st.markdown(
        """
        <style>
        .main-title  { font-size: 2.4rem; font-weight: 700; margin-bottom: 0; }
        .subtitle    { font-size: 1.1rem; color: #6b7280; margin-top: -0.5rem; }
        .score-big   { font-size: 3.5rem; font-weight: 800; text-align: center; }
        .grade-badge {
            display: inline-block; padding: 4px 16px; border-radius: 8px;
            font-weight: 700; font-size: 1.3rem; color: #fff;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<p class="main-title">🔍 CEPS Website Analyzer</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="subtitle">'
        "Content · Experience · Performance · Security — AI-powered website analysis"
        "</p>",
        unsafe_allow_html=True,
    )
    st.divider()
