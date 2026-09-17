"""
screens/architecture.py -- CodeDocAI
Architecture screen renderer (Session 7).
Static informational screen explaining the multi-agent pipeline.
"""
import streamlit as st


def render_architecture() -> None:
    # Clickable Wordmark (Acts as silent Home link, no explicit button needed)
    col_logo, _ = st.columns([1, 5], vertical_alignment="center")
    with col_logo:
        st.markdown('<div id="rail-wordmark"></div>', unsafe_allow_html=True)
        if st.button("CodeDocAI", key="arch_home_link"):
            st.session_state["current_screen"] = "landing"
            st.rerun()

    st.markdown('<hr class="nav-rail-divider">', unsafe_allow_html=True)

    st.markdown(
        '<div class="section-label">SYSTEM ARCHITECTURE</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="arch-heading">A multi-agent pipeline grounded in the source code.</div>',
        unsafe_allow_html=True,
    )

    _ARCH_STEPS = [
        (
            "01 / AST PARSING",
            "Python\u2019s built-in Abstract Syntax Tree module walks the target repository, "
            "extracting function signatures and isolating those missing docstrings without "
            "executing the code.",
            "IN: Raw .py files &rarr; OUT: Function Signatures &amp; AST Nodes",
        ),
        (
            "02 / DRAFTING ENGINE",
            "A locally fine-tuned CodeT5-small model ingests the raw source code of each "
            "undocumented function and predicts a comprehensive, formatted docstring.",
            "IN: Undocumented Nodes &rarr; OUT: Structured Docstrings",
        ),
        (
            "03 / AGENT SYNTHESIS",
            "CrewAI orchestrates a multi-agent debate to synthesize a high-level module "
            "overview, ensuring the generated documentation contextually aligns with the "
            "file\u2019s broader purpose.",
            "IN: File Context + Docstrings &rarr; OUT: Holistic Module Overview",
        ),
        (
            "04 / SEMANTIC RETRIEVAL",
            "The entire documented codebase is vectorized into ChromaDB. Questions are "
            "routed through the Gemini API, utilizing Retrieval-Augmented Generation (RAG) "
            "to ensure answers are strictly tied to actual code.",
            "IN: User Query + Vector Space &rarr; OUT: Grounded Citation",
        ),
    ]

    pipeline_html = '<div class="arch-pipeline">'
    for label, body, io_tag in _ARCH_STEPS:
        pipeline_html += (
            f'<div class="arch-step">'
            f'<span class="arch-step-label">{label}</span>'
            f'<div class="arch-step-body">'
            f'{body}'
            f'<div class="arch-io-tag">{io_tag}</div>'
            f'</div>'
            f'</div>'
        )
    pipeline_html += '</div>'
    st.markdown(pipeline_html, unsafe_allow_html=True)

    # Infrastructure Telemetry
    st.markdown(
        '<div class="arch-infra-telemetry">'
        'INFRASTRUCTURE: Local Ephemeral Execution &middot; LLM ROUTING: Gemini API &middot; VECTOR STORE: ChromaDB (In-Memory)'
        '</div>',
        unsafe_allow_html=True
    )

    # Fixed CTA Microcopy
    if st.button("INITIALIZE SCAN PIPELINE", key="cta_arch_scan"):
        st.session_state["current_screen"] = "scan"
        st.rerun()
