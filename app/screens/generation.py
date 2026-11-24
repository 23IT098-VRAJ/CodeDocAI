"""
screens/generation.py -- CodeDocAI
Generation / progress screen renderer (Phase 6 Real Pipeline Integration).
"""

import logging

import streamlit as st

from backend.pipeline import generate_overview, index_overview, run_pipeline, save_results_cache
from backend.repo.loader import cleanup_repo
from helpers import audit_event, page_heading, render_stats, session_collection_name

logger = logging.getLogger(__name__)


def completion_summary(results: dict) -> str:
    """What this run actually produced, in the numbers the coverage report holds."""
    coverage = results.get("coverage") or {}
    if not coverage.get("functions"):
        return "Overview written; ready for questions."
    drafted = coverage.get("docstrings_drafted", 0)
    noun = "docstring" if drafted == 1 else "docstrings"
    return (
        f"{drafted} {noun} drafted\u2009\u00B7\u2009coverage "
        f"{coverage.get('functions_before_pct')}% \u2192 {coverage.get('functions_after_pct')}%"
    )


def _render_complete(results: dict) -> None:
    coverage = results.get("coverage") or {}
    page_heading("Documentation ready")
    if coverage.get("functions"):
        render_stats([
            ("Coverage", f"{coverage.get('functions_before_pct')}% \u2192 {coverage.get('functions_after_pct')}%"),
            ("Docstrings drafted", coverage.get("docstrings_drafted", 0)),
            ("Overview", "Written" if results.get("overview_status") == "ok" else "Missing"),
        ], key="gen_stats")
    else:
        st.markdown(f'<p class="page-sub">{completion_summary(results)}</p>', unsafe_allow_html=True)
    with st.container(horizontal=True, gap="small", key="gen_done_actions"):
        if st.button("View docs", key="cta_view_docs", type="primary"):
            st.session_state["current_screen"] = "docs"
            st.rerun()
        if st.button("Ask a question", key="cta_gen_ask", type="secondary"):
            st.session_state["current_screen"] = "qa"
            st.rerun()


def _render_partial(results: dict) -> None:
    """Docstrings are saved but the cloud overview failed: offer the docs or a retry of the overview only."""
    page_heading("Docstrings ready, overview missing")
    st.markdown(
        '<p class="gen-error-msg">The cloud models didn’t answer. Your drafted docstrings are saved; '
        'retry the overview on its own.</p>',
        unsafe_allow_html=True,
    )

    last_error = st.session_state.get("overview_error")
    if last_error:
        st.caption(f"Last cloud error: {last_error}")

    with st.container(horizontal=True, gap="small", key="gen_partial_actions"):
        retry_clicked = st.button("Retry overview", key="cta_try_again_cloud", type="primary")
        if st.button("View docs", key="cta_view_docs_partial", type="secondary"):
            st.session_state["current_screen"] = "docs"
            st.rerun()

    if retry_clicked:
        overview_context = st.session_state.get("overview_context")
        if not overview_context:
            st.session_state["overview_error"] = "This session no longer has the scan it would retry. Start a new scan instead."
        else:
            st.session_state["generation_attempt"] = st.session_state.get("generation_attempt", 0) + 1
            # Only the overview is retried; the saved docstrings are not regenerated.
            with st.spinner("Asking the cloud for the overview again"):
                try:
                    overview = generate_overview(overview_context)
                except Exception as e:  # noqa: BLE001 - shown on the page with a retry button
                    st.session_state["overview_error"] = str(e)
                else:
                    results["overview"] = overview
                    results["overview_status"] = "ok"
                    st.session_state["pipeline_results"] = results
                    st.session_state["overview_error"] = None
                    save_results_cache(results)
                    try:
                        index_overview(overview, session_collection_name())
                    except Exception as e:  # noqa: BLE001 - the overview is still shown without the index
                        logger.warning("Could not index the overview: %s", e)
                    # The index changed, so earlier answers may no longer be the best ones.
                    st.session_state["qa_answer_cache"] = {}
        st.rerun()


def progress_line(event: dict) -> str | None:
    """One line of the live log for a pipeline event, or None for events that aren’t logged."""
    kind = event.get("type")
    if kind == "progress":
        return f"{event.get('function', 'pipeline')}: {event.get('status', 'working')}"
    if kind == "result":
        if event.get("docstring") == "(Original docstring retained)":
            return f"kept     {event.get('function')} (already documented)"
        return f"drafted  {event.get('function')}"
    return None


# Clone happened on the scan screen; the run itself walks the other four steps.
STEPS = [("clone", "Clone"), ("parse", "Parse"), ("draft", "Draft"), ("index", "Index"), ("overview", "Overview")]
_ORDER = [key for key, _ in STEPS]


def next_phase(phase: str, drafted: int, event: dict) -> tuple[str, int]:
    """The step the run is on after this pipeline event, and how many docstrings are drafted so far."""
    kind, source = event.get("type"), event.get("function", "")
    if kind == "result" and event.get("docstring") != "(Original docstring retained)":
        return "draft", drafted + 1
    if kind == "progress" and source in ("CodeT5", "Cloud fallback"):
        return "draft", drafted
    if kind == "partial":
        return "overview", drafted  # the index is written before the partial result is reported
    if kind == "progress" and source == "Repository":
        return "overview", drafted
    if kind == "done":
        return "done", drafted
    if phase == "draft" and kind == "progress" and source == "ChromaDB":
        return "index", drafted
    return phase, drafted


def progress_value(phase: str, drafted: int, total: int) -> float:
    if phase == "done":
        return 1.0
    if phase == "draft":
        return 0.15 + 0.6 * (min(drafted, total) / total if total else 1)
    return {"clone": 0.0, "parse": 0.08, "index": 0.8, "overview": 0.88}.get(phase, 0.0)


def phase_label(phase: str, drafted: int, total: int) -> str:
    return {
        "parse": "Parsing files",
        "draft": f"Drafting docstrings {min(drafted, total)}/{total}" if total else "Drafting docstrings",
        "index": "Indexing for questions",
        "overview": "Writing the overview",
        "done": "Done",
    }.get(phase, "Working")


def step_tracker(phase: str, drafted: int, total: int) -> str:
    """Clone → Parse → Draft n/N → Index → Overview, each marked done, current or waiting."""
    current = len(_ORDER) if phase == "done" else _ORDER.index(phase) if phase in _ORDER else 0
    items = []
    for index, (key, label) in enumerate(STEPS):
        state = "done" if index < current else "current" if index == current else "waiting"
        text = f"{label} {min(drafted, total)}/{total}" if key == "draft" and total else label
        marker = "✓" if state == "done" else str(index + 1)
        aria = ' aria-current="step"' if state == "current" else ""
        items.append(f'<li class="gen-step gen-step-{state}"{aria}><span class="gen-step-marker">{marker}</span>{text}</li>')
    return f'<ol class="gen-steps">{"".join(items)}</ol>'


def render_generation() -> None:
    # Force-hide Stale Scan UI. Style-only HTML goes to Streamlit's event container, outside the page flow.
    st.html(
        '<style>'
        'div.element-container:has(#ghost-scan-results), '
        'div.element-container:has(#ghost-scan-estimate), '
        '.st-key-scan_source, .st-key-cta_generate_docs, .st-key-cta_scan_view_docs '
        '{ display: none !important; height: 0 !important; opacity: 0 !important; margin: 0 !important; padding: 0 !important; }'
        '</style>'
    )

    # If generation already finished, show its outcome instead of running again
    if st.session_state.get("generation_complete", False):
        results = st.session_state.get("pipeline_results") or {}
        if results.get("overview_status") == "skipped":
            _render_partial(results)
        else:
            _render_complete(results)
        return

    page_heading("Generating documentation")

    # Grab the target repo source populated by your loader
    repo_source = st.session_state.get("repo_source")
    if not repo_source:
        st.error("There’s no scanned repository in this session. Run a scan first.")
        if st.button("Back to scan", key="gen_back_to_scan", type="primary"):
            st.session_state["current_screen"] = "scan"
            st.rerun()
        return

    total_to_draft = (st.session_state.get("scan_summary") or {}).get("missing_count", 0)
    tracker_slot = st.empty()
    progress_slot = st.empty()
    with st.expander("Details", type="compact", key="compact_gen_details"):
        log_slot = st.empty()
    log_lines = []
    finished = False
    phase, drafted = "parse", 0
    st.session_state["qa_answer_cache"] = {}  # answers from a previous index no longer apply

    def show() -> None:
        tracker_slot.markdown(step_tracker(phase, drafted, total_to_draft), unsafe_allow_html=True)
        progress_slot.progress(progress_value(phase, drafted, total_to_draft), text=phase_label(phase, drafted, total_to_draft))
        log_slot.code("\n".join(log_lines[-12:]) or "Starting", language="plaintext")

    show()
    events = run_pipeline(
        repo_source,
        ai_engine=st.session_state.get("ai_engine"),
        collection_name=session_collection_name(),
    )
    for event in events:
        e_type = event.get("type")
        phase, drafted = next_phase(phase, drafted, event)

        line = progress_line(event)
        if line:
            log_lines.append(line)
        elif e_type == "partial":
            # Local work is safe from here on, whatever happens to the cloud call.
            st.session_state["pipeline_results"] = event["data"]
            st.session_state["overview_context"] = event.get("overview_context", "")
        elif e_type == "rate_limited":
            st.session_state["overview_error"] = event.get("message")
            finished = True
            break
        elif e_type == "error":
            st.error(event.get("message"))
            return
        elif e_type == "done":
            st.session_state["pipeline_results"] = event
            st.session_state["overview_error"] = None
            finished = True
            break
        show()

    if finished:
        st.session_state["generation_complete"] = True
        results = st.session_state.get("pipeline_results") or {}
        coverage = results.get("coverage") or {}
        audit_event(
            "DOC_GENERATION",
            f"Drafted {coverage.get('docstrings_drafted', 0)} docstrings with the local CodeT5 engine; "
            f"function coverage {coverage.get('functions_before_pct')}% -> {coverage.get('functions_after_pct')}%; "
            f"architecture overview {'generated' if results.get('overview_status') == 'ok' else 'skipped (cloud unreachable)'}.",
        )
        # Everything needed is now in session memory, so the source copy on disk can go.
        cleanup_repo(repo_source.get("local_path"))
        st.rerun()
