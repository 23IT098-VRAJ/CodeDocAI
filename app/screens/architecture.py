"""
screens/architecture.py -- CodeDocAI
Architecture screen renderer (Session 7).
Static informational screen explaining what happens to a scanned repository.
"""
import streamlit as st

from helpers import page_heading


def render_architecture() -> None:
    page_heading("How it works", "What happens to your code, step by step.")

    _ARCH_STEPS = [
        (
            "Parse",
            "Python’s ast module walks each .py file and pulls out its functions, methods "
            "and classes, noting which ones lack a docstring. It reads the code; it never runs it.",
            ".py files &rarr; functions with and without docstrings",
        ),
        (
            "Draft",
            "A CodeT5-small model, fine-tuned for this job and running on your machine, reads "
            "each undocumented function and drafts a one-line docstring. CodeDocAI then writes "
            "those drafts into a copy of your files.",
            "undocumented functions &rarr; drafted docstrings, documented files",
        ),
        (
            "Overview",
            "A CrewAI agent gets an outline of every file (function names plus the first line "
            "of each docstring) and writes the repository overview in a single cloud request.",
            "file outlines &rarr; repository overview",
        ),
        (
            "Answer",
            "ChromaDB indexes the functions, the file summaries and the overview in memory. "
            "For each question, the four closest entries go to the model with the question, "
            "and the citations come from those entries.",
            "question + 4 retrieved entries &rarr; answer with citations",
        ),
    ]

    pipeline_html = '<ol class="arch-pipeline">'
    for label, body, io_tag in _ARCH_STEPS:
        pipeline_html += (
            f'<li class="arch-step">'
            f'<span class="arch-step-label">{label}</span>'
            f'<div class="arch-step-body">'
            f'{body}'
            f'<div class="arch-io-tag">{io_tag}</div>'
            f'</div>'
            f'</li>'
        )
    pipeline_html += '</ol>'
    st.markdown(pipeline_html, unsafe_allow_html=True)

    # Where each part runs
    st.markdown(
        '<div class="arch-infra-telemetry">'
        '<span class="arch-infra-item">Cloud: Gemini, Groq as backup</span>'
        '<span class="arch-infra-item">Index: ChromaDB, in memory</span>'
        '</div>',
        unsafe_allow_html=True
    )

    with st.container(horizontal=True, vertical_alignment="center", key="arch_actions"):
        if st.button("Start a scan", key="cta_arch_scan", type="primary"):
            st.session_state["current_screen"] = "scan"
            st.rerun()
        if st.button("Back", key="arch_back", type="tertiary", icon=":material/arrow_back:"):
            st.session_state["current_screen"] = "landing"
            st.rerun()
