"""
screens/generation.py -- CodeDocAI
Generation / progress screen renderer (Phase 6 Real Pipeline Integration).
"""

import inspect
import streamlit as st

try:
    from helpers import render_nav_rail
except ImportError:
    from app.helpers import render_nav_rail

# Import the real pipeline orchestrator
from backend.pipeline import run_pipeline


def _invoke_pipeline(repo_source):
    """
    Invokes run_pipeline while passing the cached CodeT5 engine if
    the backend pipeline function accepts it.
    """
    ai_engine = st.session_state.get("ai_engine")
    sig = inspect.signature(run_pipeline)
    
    if "ai_engine" in sig.parameters or any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()):
        return run_pipeline(repo_source, ai_engine=ai_engine)
    return run_pipeline(repo_source)


def render_generation() -> None:
    # Shared Top Navigation Rail
    render_nav_rail("generation")

    # Force-hide Stale Scan UI
    st.markdown(
        '<style>'
        'div.element-container:has(#ghost-scan-results), '
        'div.element-container:has(#ghost-scan-estimate), '
        'div.element-container:has(#cta-generate-marker), '
        'div.element-container:has(#cta-generate-marker) + div.element-container, '
        'div.element-container:has(#cta-secondary-marker), '
        'div.element-container:has(#cta-secondary-marker) + div.element-container '
        '{ display: none !important; height: 0 !important; opacity: 0 !important; margin: 0 !important; padding: 0 !important; }'
        '</style>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="section-label">GENERATING DOCUMENTATION</div>', unsafe_allow_html=True)

    # If generation already completed successfully, skip directly to success state
    if st.session_state.get("generation_complete", False):
        st.markdown('<p class="gen-intro">Documentation has been generated for this codebase.</p>', unsafe_allow_html=True)
        outcome_html = (
            '<div class="gen-outcome-section">'
            '<div class="gen-outcome-label">GENERATION COMPLETE</div>'
            '<p class="gen-outcome-sub">Successfully drafted docstrings and synthesized module overviews. Vector embeddings stored in session memory for RAG Q&A.</p>'
            '</div>'
        )
        st.markdown(outcome_html, unsafe_allow_html=True)
        st.markdown('<div id="cta-view-docs-marker"></div>', unsafe_allow_html=True)
        if st.button("VIEW DOCUMENTATION", key="cta_view_docs"):
            st.session_state["current_screen"] = "docs"
            st.rerun()
        return

    # Grab the target repo source populated by your loader
    repo_source = st.session_state.get("repo_source")
    if not repo_source:
        st.error("No valid repository source found in session. Please run a scan first.")
        if st.button("← RETURN TO SCAN"):
            st.session_state["current_screen"] = "scan"
            st.rerun()
        return

    st.markdown('<p class="gen-intro">Parsing AST nodes &middot; drafting docstrings via CodeT5 &middot; building vector index.</p>', unsafe_allow_html=True)
    st.markdown(
        '<div class="telemetry-grid">'
        '<div class="telemetry-col"><span class="tel-label">ENGINE</span><span class="tel-value">CodeT5-small (Local)</span></div>'
        '<div class="telemetry-col"><span class="tel-label">ORCHESTRATION</span><span class="tel-value">CrewAI Multi-Agent</span></div>'
        '<div class="telemetry-col"><span class="tel-label">VECTOR STATE</span><span class="tel-value">Initializing ChromaDB...</span></div>'
        '</div>',
        unsafe_allow_html=True,
    )

    # -- Live Progress Feed via st.empty() (Phase 6 Compliant) --
    status_container = st.empty()
    log_lines = []
    
    pipeline_data = None
    rate_limited = False

    # Run the generator directly in the main thread
    with st.spinner("Executing Multi-Agent Documentation Pipeline..."):
        for event in _invoke_pipeline(repo_source):
            e_type = event.get("type")
            
            if e_type == "progress":
                log_lines.append(f"⏳ {event.get('function', 'System')}: {event.get('status', 'processing')}")
            elif e_type == "result":
                log_lines.append(f"✅ {event.get('function')} docstring drafted.")
            elif e_type == "rate_limited":
                rate_limited = True
                break
            elif e_type == "error":
                st.error(event.get("message"))
                return
            elif e_type == "done":
                pipeline_data = event
                break

            # Keep only the last 8 lines on screen to mimic a snug terminal height
            display_logs = "\n".join(log_lines[-8:])
            status_container.code(display_logs, language="plaintext")

    status_container.empty()

    # -- Handle Outcomes --
    if rate_limited:
        outcome_html = (
            '<div class="gen-outcome-section">'
            '<p class="gen-error-msg">'
            "Gemini\u2019s free-tier rate limit was hit while synthesizing the module overview. "
            "Try again in a moment."
            '</p>'
            '</div>'
        )
        st.markdown(outcome_html, unsafe_allow_html=True)
        st.markdown('<div id="cta-try-again-marker"></div>', unsafe_allow_html=True)
        if st.button("TRY AGAIN", key="cta_try_again"):
            st.session_state["generation_attempt"] = st.session_state.get("generation_attempt", 0) + 1
            st.rerun()
            
    elif pipeline_data:
        # Securely anchor data in the main thread before rerunning
        st.session_state["pipeline_results"] = pipeline_data
        st.session_state["generation_complete"] = True

        outcome_html = (
            '<div class="gen-outcome-section">'
            '<div class="gen-outcome-label">GENERATION COMPLETE</div>'
            '<p class="gen-outcome-sub">Successfully drafted docstrings and synthesized module overviews. Vector embeddings stored in session memory for RAG Q&A.</p>'
            '</div>'
        )
        st.markdown(outcome_html, unsafe_allow_html=True)
        st.markdown('<div id="cta-view-docs-marker"></div>', unsafe_allow_html=True)
        
        if st.button("VIEW DOCUMENTATION", key="cta_view_docs"):
            st.session_state["current_screen"] = "docs"
            st.rerun()