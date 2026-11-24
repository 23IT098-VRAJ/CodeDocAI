"""
screens/landing.py -- CodeDocAI
Landing screen renderer. The shared top bar (wordmark, How it works, sign-in) is
drawn by app.py above every screen.
"""

import streamlit as st

from components import code_window

_TRUST_POINTS = [
    ("Read, never run", "Your code is parsed, not executed."),
    ("Deleted after generation", "The copy of your repo doesn’t outlive the run."),
    ("Only outlines leave", "The cloud sees an outline and four passages per question."),
    ("Secrets redacted first", "Keys and tokens are replaced before anything is sent."),
]

_STEPS = [
    ("Scan", "Parse every file with ast."),
    ("Draft", "CodeT5 writes the missing docstrings locally."),
    ("Overview", "One cloud request maps the repo."),
    ("Ask", "Answers cite the function they came from."),
]

_TAGS = ["CodeT5-small", "CrewAI", "ChromaDB", "Gemini API", "RAG", "Python ast"]


def render_landing() -> None:
    # ---- Hero: text left, editor right ----
    col_hero_text, col_hero_vis = st.columns([1.2, 1], gap="large", vertical_alignment="center")
    with col_hero_text:
        st.markdown(
            '<div class="hero">'
            '<h1 class="hero-headline">Docstrings for the functions nobody got around to documenting.</h1>'
            '<p class="hero-subhead">Drafts missing docstrings on your machine, writes them into your '
            'files, and answers questions with citations.</p>'
            '</div>',
            unsafe_allow_html=True,
        )
        if st.button("Start a scan", key="cta_hero", type="primary"):
            st.session_state["current_screen"] = "scan"
            st.rerun()

    with col_hero_vis:
        code_window.render()

    # ---- Trust row ----
    trust_html = '<div class="security-bar">'
    for title, line in _TRUST_POINTS:
        trust_html += f'<div class="security-item"><h2>{title}</h2><p>{line}</p></div>'
    trust_html += '</div>'
    st.markdown(trust_html, unsafe_allow_html=True)

    # ---- Steps + built with ----
    card_html = '<div class="process-card"><h2 class="landing-h2">How it works</h2><ol class="timeline">'
    for step, desc in _STEPS:
        card_html += (
            '<li class="timeline-item">'
            f'<span class="timeline-step">{step}</span>'
            f'<span class="timeline-desc">{desc}</span>'
            '</li>'
        )
    card_html += '</ol><div class="built-tags" aria-label="Built with">'
    card_html += "".join(f'<span class="built-tag">{tag}</span>' for tag in _TAGS)
    card_html += '</div></div>'
    st.markdown(card_html, unsafe_allow_html=True)

    # ---- Closing CTA ----
    st.markdown(
        '<div class="closing-section"><p class="closing-label">Scan a repository from GitHub or a .zip.</p></div>',
        unsafe_allow_html=True,
    )
    with st.container(horizontal=True, horizontal_alignment="center", key="closing_cta"):
        if st.button("Start a scan", key="cta_closing", type="secondary"):
            st.session_state["current_screen"] = "scan"
            st.rerun()
