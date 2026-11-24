"""
screens/generation.py -- CodeDocAI
Generation / progress screen renderer (Phase 6 Real Pipeline Integration).
"""

import html
import logging
import time

import streamlit as st

from backend.pipeline import MAX_LOCAL_DRAFTS, generate_overview, index_overview, run_pipeline, save_results_cache
from backend.repo.loader import cleanup_repo
from components import overview_loader
from components.index_loader import index_loader_html
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


def _repo_label() -> str:
    url = (st.session_state.get("scan_github_url") or "").strip().rstrip("/")
    if url.startswith("http") and url.count("/") >= 4:
        return "/".join(url.removesuffix(".git").split("/")[-2:])
    return "your upload"


def _coverage_card(files: list[dict]) -> str:
    rows = []
    for row in sorted(files, key=lambda r: r.get("functions", 0), reverse=True)[:8]:
        total = row.get("functions", 0)
        if not total:
            continue
        before, after = row.get("functions_before", 0), row.get("functions_after", 0)
        rows.append(
            '<li class="cov-row">'
            f'<span class="cov-path">{html.escape(row.get("path", ""))}</span>'
            f'<span class="cov-bar" aria-hidden="true"><i class="after" style="width:{after / total:.0%}"></i>'
            f'<i class="before" style="width:{before / total:.0%}"></i></span>'
            f'<span class="cov-num">{before} → {after} of {total}</span>'
            '</li>'
        )
    more = len([r for r in files if r.get("functions")]) - len(rows)
    tail = f'<p class="done-note">and {more} more file{"s" if more != 1 else ""} in Docs</p>' if more > 0 else ""
    return (
        '<section class="done-card"><h2 class="done-h">Coverage by file</h2>'
        '<p class="done-legend"><i class="before"></i>before <i class="after"></i>after</p>'
        f'<ul class="cov-list">{"".join(rows)}</ul>{tail}</section>'
    )


def _found_card(coverage: dict, functions: list[dict]) -> str:
    """What the scan found: how the functions split between documented, drafted and still missing."""
    total = coverage.get("functions", 0)
    if not total:
        return ""
    before = coverage.get("functions_before", 0)
    drafted = coverage.get("docstrings_drafted", 0)
    missing = max(total - coverage.get("functions_after", 0), 0)
    segments = "".join(
        f'<i class="{cls}" style="width:{count / total:.1%}"></i>'
        for cls, count in (("before", before), ("drafted", drafted), ("missing", missing)) if count
    )
    kinds = {kind: sum(1 for fn in functions if fn.get("kind") == kind) for kind in ("function", "method", "class")}
    by_cloud = sum(1 for fn in functions if fn.get("doc_status") == "cloud")
    files = coverage.get("file_count", 0)
    facts = [
        (kinds["function"], "top-level functions"),
        (kinds["method"], "methods inside classes"),
        (kinds["class"], "classes (drafting covers their methods)"),
        (f"{coverage.get('files_with_module_docstring', 0)} / {files}", "files with a module docstring"),
        (drafted - by_cloud, "docstrings written by our CodeT5"),
    ]
    if by_cloud:
        facts.append((by_cloud, "written by the cloud fallback"))
    rows = "".join(f"<li><b>{html.escape(str(value))}</b>{html.escape(label)}</li>" for value, label in facts)
    legend = (f'<p class="done-legend"><i class="before"></i>documented before {before}'
              f'<i class="drafted"></i>drafted now {drafted}'
              + (f'<i class="missing"></i>still missing {missing}' if missing else "") + "</p>")
    return (
        '<section class="done-card"><h2 class="done-h">What the scan found</h2>'
        f'<div class="split-bar" aria-hidden="true">{segments}</div>{legend}'
        f'<ul class="found-list">{rows}</ul></section>'
    )


def _longest_card(functions: list[dict], limit: int = 5) -> str:
    """The biggest functions that now have a docstring: where a reader needed one most."""
    drafted = sorted(
        (fn for fn in functions if fn.get("doc_status") in ("local", "cloud") and fn.get("loc")),
        key=lambda fn: fn.get("loc", 0), reverse=True,
    )[:limit]
    if not drafted:
        return ""
    longest = drafted[0].get("loc", 1)
    rows = "".join(
        '<li class="long-row">'
        f'<span class="long-name">{html.escape(fn.get("name", ""))}</span>'
        f'<span class="long-file">{html.escape(fn.get("file", ""))}</span>'
        f'<span class="long-bar" aria-hidden="true"><i style="width:{fn.get("loc", 0) / longest:.0%}"></i></span>'
        f'<span class="long-loc">{fn.get("loc", 0)} lines</span>'
        '</li>'
        for fn in drafted
    )
    return ('<section class="done-card done-wide"><h2 class="done-h">Longest functions, now documented</h2>'
            f'<ul class="long-list">{rows}</ul></section>')


def _render_complete(results: dict) -> None:
    coverage = results.get("coverage") or {}
    timing = st.session_state.get("generation_timing") or {}
    functions = results.get("functions") or []
    files = coverage.get("file_count") or len({fn.get("file") for fn in functions})
    subtitle = f"{_repo_label()} · {files} file{'s' if files != 1 else ''}"
    if timing.get("total"):
        subtitle += f" · finished in {timing['total']:.0f} s"
    page_heading("Documentation ready", subtitle)

    if coverage.get("functions"):
        stats = [
            ("Coverage", f"{coverage.get('functions_before_pct')}% → {coverage.get('functions_after_pct')}%"),
            ("Docstrings drafted", coverage.get("docstrings_drafted", 0)),
            ("Functions scanned", coverage.get("functions", 0)),
        ]
        if timing.get("draft") and timing.get("drafted"):
            stats.append(("Per docstring", f"{timing['draft'] / timing['drafted']:.2f} s"))
        stats.append(("Overview", "Written" if results.get("overview_status") == "ok" else "Missing"))
        render_stats(stats, key="gen_stats", count_up=True)
        left = coverage.get("functions", 0) - coverage.get("functions_after", 0)
        if coverage.get("docstrings_drafted", 0) >= MAX_LOCAL_DRAFTS and left > 0:
            st.caption(f"Drafting stops at {MAX_LOCAL_DRAFTS:,} functions per scan; {left:,} still have no docstring.")
    else:
        st.markdown(f'<p class="page-sub">{completion_summary(results)}</p>', unsafe_allow_html=True)
    with st.container(horizontal=True, gap="small", key="gen_done_actions"):
        if st.button("View docs", key="cta_view_docs", type="primary"):
            st.session_state["current_screen"] = "docs"
            st.rerun()
        if st.button("Ask a question", key="cta_gen_ask", type="secondary"):
            st.session_state["current_screen"] = "qa"
            st.rerun()

    if coverage.get("functions"):
        st.html(
            '<div class="done-grid">'
            + _coverage_card(coverage.get("files") or [])
            + _found_card(coverage, functions)
            + '</div>'
            + _longest_card(functions)
        )


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
        if event.get("function") == "Repository":
            return None  # the overview loader replaces the log at this point
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
    if kind == "progress" and source == "Index" and "total" in event:
        return "index", drafted  # the batched embedding after drafting (the first "Index" line is a warm-up)
    if phase == "draft" and kind == "progress" and source == "ChromaDB":
        return "index", drafted
    return phase, drafted


def progress_value(phase: str, drafted: int, total: int, indexed: tuple[int, int] = (0, 0)) -> float:
    if phase == "done":
        return 1.0
    if phase == "draft":
        return 0.15 + 0.6 * (min(drafted, total) / total if total else 1)
    if phase == "index" and indexed[1]:
        return 0.75 + 0.13 * indexed[0] / indexed[1]
    return {"clone": 0.0, "parse": 0.08, "index": 0.75, "overview": 0.88}.get(phase, 0.0)


def phase_label(phase: str, drafted: int, total: int, indexed: tuple[int, int] = (0, 0)) -> str:
    return {
        "parse": "Parsing files",
        "draft": f"Drafting docstrings {min(drafted, total)}/{total}" if total else "Drafting docstrings",
        "index": f"Indexing for questions {indexed[0]}/{indexed[1]}" if indexed[1] else "Indexing for questions",
        "overview": "Writing the overview",
        "done": "Done",
    }.get(phase, "Working")


_CHECK = ('<svg class="gen-check" viewBox="0 0 16 16" aria-hidden="true">'
          '<path d="M3.5 8.5l3 3 6-7" fill="none" stroke="currentColor" stroke-width="2" '
          'stroke-linecap="round" stroke-linejoin="round"/></svg><span class="sr-only">done</span>')


def step_tracker(phase: str, drafted: int, total: int) -> str:
    """Clone → Parse → Draft n/N → Index → Overview, each marked done, current or waiting."""
    current = len(_ORDER) if phase == "done" else _ORDER.index(phase) if phase in _ORDER else 0
    items = []
    for index, (key, label) in enumerate(STEPS):
        state = "done" if index < current else "current" if index == current else "waiting"
        text = f"{label} {min(drafted, total)}/{total}" if key == "draft" and total else label
        marker = _CHECK if state == "done" else str(index + 1)
        aria = ' aria-current="step"' if state == "current" else ""
        latest = " gen-step-latest" if state == "done" and index == current - 1 else ""
        items.append(f'<li class="gen-step gen-step-{state}{latest}"{aria}><span class="gen-step-marker">{marker}</span>{text}</li>')
    return f'<ol class="gen-steps">{"".join(items)}</ol>'


def render_generation() -> None:
    # Force-hide Stale Scan UI. Style-only HTML goes to Streamlit's event container, outside the page flow.
    st.html(
        '<style>'
        'div.element-container:has(#ghost-scan-results), '
        'div.element-container:has(#ghost-scan-estimate), '
        '.st-key-scan_source, .st-key-cta_generate_docs, .st-key-cta_scan_view_docs, '
        # Anything still marked stale here is left over from the scan screen (this run is long,
        # so Streamlit would keep showing it until generation ends, e.g. the "Skipped:" note).
        '[data-stale="true"] '
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
    details_slot = st.empty()
    with details_slot.container(), st.expander("Details", expanded=True, type="compact", key="compact_gen_details"):
        log_slot = st.empty()
    log_lines = []
    loader_started = None  # set once the overview loader replaces the details panel
    run_started, draft_started, draft_seconds = time.monotonic(), None, None
    indexed = (0, 0)  # entries embedded so far, of how many
    index_started, index_pct = None, 0.0  # when the index loader took over, and its last percentage
    finished = False
    phase, drafted = "parse", 0
    st.session_state["qa_answer_cache"] = {}  # answers from a previous index no longer apply

    def show() -> None:
        tracker_slot.markdown(step_tracker(phase, drafted, total_to_draft), unsafe_allow_html=True)
        # Only Parse keeps a label: Draft's count is already in the step tracker above, and Index
        # and Overview have their own loading screen with the same words in large type.
        label = phase_label(phase, drafted, total_to_draft, indexed) if phase == "parse" else None
        progress_slot.progress(progress_value(phase, drafted, total_to_draft, indexed), text=label)
        if loader_started is None and index_started is None:
            log_slot.code("\n".join(log_lines) or "Starting", language="plaintext", height=344)  # 15 lines of 20.8 px + 32 px padding

    show()
    events = run_pipeline(
        repo_source,
        ai_engine=st.session_state.get("ai_engine"),
        collection_name=session_collection_name(),
    )
    for event in events:
        e_type = event.get("type")
        phase, drafted = next_phase(phase, drafted, event)
        if phase == "draft" and draft_started is None:
            draft_started = time.monotonic()
        # Drafting ends where indexing starts; the time per docstring covers the model's work only.
        if phase in ("index", "overview", "done") and draft_started is not None and draft_seconds is None:
            draft_seconds = time.monotonic() - draft_started
        if e_type == "progress" and event.get("function") == "Index" and "total" in event:
            indexed = (event.get("done", 0), event["total"])
            # Drafting is over: the details panel becomes the index loader, redrawn per batch.
            if index_started is None:
                index_started = time.monotonic()
            with details_slot.container():
                st.html(index_loader_html(indexed[0], indexed[1], index_pct, time.monotonic() - index_started))
            index_pct = 100 * indexed[0] / indexed[1] if indexed[1] else 100.0
        if loader_started is None and e_type == "progress" and event.get("function") == "Repository":
            # The overview is one cloud request that can take a while: show what is happening.
            with details_slot.container():
                loader_started = overview_loader.render(repo_source.get("py_files", []))

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
        total_seconds = time.monotonic() - run_started
        if loader_started is not None:
            overview_loader.wait_for_cycle_end(loader_started)  # never cut the animation mid-loop
        st.session_state["generation_timing"] = {"total": total_seconds, "draft": draft_seconds, "drafted": drafted}
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
