"""
screens/scan.py -- CodeDocAI
Scan screen renderer with Tabbed UI and Live Backend Streaming.
"""

import html as _html
import logging
import math as _math
import tempfile
from pathlib import Path

import streamlit as st

from backend.parser.extractor import extract_definitions
from backend.repo.loader import (
    TEMP_PREFIX,
    RepoValidationError,
    cleanup_repo,
    clone_github_repo,
    extract_zip,
    read_source,
)
from helpers import audit_event, new_scan_button, page_heading, render_stats

logger = logging.getLogger(__name__)

SOURCE_MODES = ["GitHub URL", "Upload .zip"]


def estimate_generation_time(missing_count: int) -> str:
    """
    Rough wall-clock estimate for the generation step: batched CodeT5 drafting on a
    CPU (about 0.3 s per function, measured at under 0.2 s) plus a fixed allowance
    for loading the vector index and one cloud request for the overview.
    """
    seconds = 20 + 0.3 * missing_count
    if seconds < 60:
        return "under a minute"
    return f"~{_math.ceil(seconds / 60)} min"


def render_scan() -> None:
    # -- Prevent Ghosting --
    if st.session_state.get("current_screen", "scan") != "scan":
        return

    status = st.session_state.get("scan_status", "idle")

    # =====================================================================
    # INPUT STATE
    # =====================================================================
    if status != "populated":
        page_heading("New scan")

        source_mode = st.segmented_control(
            "Source", SOURCE_MODES, default=SOURCE_MODES[0], required=True,
            key="scan_source_mode", label_visibility="collapsed",
        ) or SOURCE_MODES[0]
        github_url, uploaded_file = "", None
        error_field = st.session_state.get("scan_error_field")
        # One form: the click sends the pasted URL with it. As separate widgets, the URL was
        # committed by its own rerun on blur, and a click landing during that rerun was lost.
        # The form and, once it is sent, the scan status share one slot: the status replaces the
        # form, so the old form is never left on the page while the scan runs.
        form_slot = st.empty()
        with form_slot.container(), st.form("scan_form", border=False, enter_to_submit=True):
            with st.container(border=True, key="scan_source_card"):
                if source_mode == SOURCE_MODES[0]:
                    github_url = st.text_input(
                        "GitHub repository URL",
                        placeholder="https://github.com/owner/repository",
                        key="scan_github_url_input",
                    )
                    hint = "Public repository · Python · up to 100 MB and 500 files"
                else:
                    uploaded_file = st.file_uploader("Project .zip", type=["zip"], key="scan_file_upload")
                    hint = "A .zip of the project · Python · up to 100 MB and 500 files. Works for private code."
                # An error sits under the field it is about; role="alert" announces it to screen readers.
                if status == "error" and error_field == ("url" if source_mode == SOURCE_MODES[0] else "zip"):
                    err_msg = st.session_state.get("scan_error_message", "The scan failed.")
                    st.markdown(f'<p class="scan-error-line" role="alert">{_html.escape(err_msg)}</p>',
                                unsafe_allow_html=True)
                else:
                    st.caption(hint)
            submitted = st.form_submit_button("Scan repository", key="cta_scan_repo", type="primary")

        # Trigger Backend Pipeline
        if submitted:
            has_zip = uploaded_file is not None
            has_url = bool(github_url and github_url.strip())

            if not has_zip and not has_url:
                st.session_state["scan_status"] = "error"
                st.session_state["scan_error_field"] = "url" if source_mode == SOURCE_MODES[0] else "zip"
                st.session_state["scan_error_message"] = (
                    "Paste a GitHub URL first." if source_mode == SOURCE_MODES[0] else "Choose a .zip first."
                )
                st.rerun()

            temp_dir = tempfile.mkdtemp(prefix=TEMP_PREFIX)
            repo_source = None

            try:
                with form_slot.container(), st.container(key="scan_status"), \
                        st.status("Scanning the repository", expanded=True) as status_box:
                    # 1. Loading Phase
                    if has_zip:
                        status_box.write(f"Extracting `{uploaded_file.name}`")
                        uploaded_file.seek(0)
                        repo_source = extract_zip(uploaded_file, temp_dir)
                        st.session_state["scan_github_url"] = uploaded_file.name
                    else:
                        clean_url = github_url.strip()
                        status_box.write(f"Cloning `{clean_url}`")
                        repo_source = clone_github_repo(clean_url, temp_dir)
                        st.session_state["scan_github_url"] = clean_url

                    st.session_state["repo_source"] = repo_source

                    local_path = repo_source.get("local_path", "")
                    py_files = repo_source.get("py_files", [])

                    # Pre-calculate file function totals so the ledger renders correctly
                    # Calculate AST statistics without running heavy generation pipeline
                    ledger_results = []
                    definitions_by_file = {}
                    total_missing = 0
                    total_functions = 0

                    for rel_p in py_files:
                        norm_p = rel_p.replace("\\", "/")
                        status_box.write(f"Parsing `{norm_p}`")

                        try:
                            content = read_source(Path(local_path, rel_p))
                            definitions = extract_definitions(content, norm_p)
                            definitions_by_file[norm_p] = definitions  # the pipeline reuses these
                            funcs = [d for d in definitions if d["kind"] != "class"]
                            func_count = len(funcs)
                            missing_count = sum(1 for fn in funcs if not fn.get("has_docstring", False))

                            if func_count > 0:
                                ledger_results.append({
                                    "path": norm_p,
                                    "functions": func_count,
                                    "missing": missing_count,
                                })
                                total_functions += func_count
                                total_missing += missing_count
                        except Exception as error:  # noqa: BLE001 - one unreadable file must not fail the scan
                            logger.warning("Could not parse %s: %s", norm_p, error)

                    repo_source["definitions"] = definitions_by_file
                    file_count = len(ledger_results)
                    st.session_state["scan_results"] = ledger_results
                    st.session_state["scan_summary"] = {
                        "file_count": file_count,
                        "missing_count": total_missing,
                    }
                    st.session_state["scan_status"] = "populated"
                    st.session_state["scan_error_message"] = None
                    audit_event(
                        "REPO_SCAN",
                        f"Scanned '{st.session_state['scan_github_url']}': {file_count} files with functions, "
                        f"{total_functions} functions, {total_missing} missing docstrings.",
                    )
                    status_box.update(label="Scan finished", state="complete", expanded=False)
                    st.rerun()

            except RepoValidationError as e:
                cleanup_repo(temp_dir)
                st.session_state["repo_source"] = None
                st.session_state["scan_status"] = "error"
                st.session_state["scan_error_field"] = "zip" if has_zip else "url"
                st.session_state["scan_error_message"] = str(e)
                st.rerun()
            except Exception as e:  # noqa: BLE001 - shown to the visitor under the field that caused it
                cleanup_repo(temp_dir)
                st.session_state["repo_source"] = None
                st.session_state["scan_status"] = "error"
                st.session_state["scan_error_field"] = "zip" if has_zip else "url"
                st.session_state["scan_error_message"] = f"The scan failed: {e}"
                st.rerun()

    # =====================================================================
    # RESULTS STATE
    # =====================================================================
    else:
        page_heading("Scan results")

        source_name = st.session_state.get("scan_github_url", "").strip() or "Uploaded .zip"
        source_name = source_name.removeprefix("https://github.com/")
        with st.container(horizontal=True, vertical_alignment="center", gap="small", key="scan_source"):
            st.markdown(f'<span class="repo-chip">{_html.escape(source_name)}</span>',
                        unsafe_allow_html=True, width="content")
            # The reset itself deletes the scanned copy, so repo_source must still be set when it runs.
            new_scan_button("New scan", key="cta_scan_reset", type="tertiary", icon=":material/refresh:")

        results = st.session_state.get("scan_results", [])

        # Removed redundant error display from here.
        # Only rendering the success ledger:
        if status == "populated" and results is not None:
            summary = st.session_state.get("scan_summary") or {}
            file_count = summary.get("file_count", len(results))
            missing_count = summary.get("missing_count", 0)

            # Once documentation has been generated, the ledger shows what is documented
            # now, not what was missing when the repository was scanned.
            coverage = (st.session_state.get("pipeline_results") or {}).get("coverage") or {}
            generated = bool(st.session_state.get("generation_complete")) and bool(coverage.get("files"))
            if generated:
                documented = {row["path"]: row["functions_after"] for row in coverage["files"]}
                results = [
                    {**row, "missing": max(0, row.get("functions", 0) - documented[row["path"]])}
                    if row["path"] in documented else row
                    for row in results
                ]
                missing_count = sum(row["missing"] for row in results)

            stats = [("Files", file_count)]
            if generated:
                stats += [("Drafted", coverage.get("docstrings_drafted", 0)), ("Still missing", missing_count)]
            else:
                stats += [("Missing docstrings", missing_count)]
                if missing_count:
                    stats.append(("To generate, about", estimate_generation_time(missing_count)))
            render_stats(stats, key="scan_stats")
            ledger_html = '<div id="ghost-scan-results" class="scan-results-section">'

            for i, row in enumerate(results):
                idx_str = str(i + 1).zfill(2)
                path = row["path"]
                funcs = row.get("functions", 0)
                missing = row["missing"]

                if missing == 0:
                    pip_color = "pip-green"
                elif missing >= funcs and funcs > 0:
                    pip_color = "pip-red"
                else:
                    pip_color = "pip-amber"

                if missing > 0:
                    meta_class = "ledger-meta-missing"
                    meta_text = f'{missing} of {funcs} missing'
                else:
                    meta_class = "ledger-meta-clean"
                    meta_text = f'{funcs} documented'

                ledger_html += (
                    f'<div class="ledger-row">'
                    f'<div class="ledger-index"><span class="severity-pip {pip_color}"></span>{idx_str}</div>'
                    f'<span class="ledger-path">{path}</span>'
                    f'<span class="{meta_class}">{meta_text}</span>'
                    f'</div>'
                )
            ledger_html += '</div>'
            st.markdown(ledger_html, unsafe_allow_html=True)

            st.caption("Skipped: `__init__.py`, tests, virtual environments and hidden folders.")
            if not generated and missing_count == 0:
                st.markdown(
                    '<p class="scan-estimate-clean">Every function already has a docstring, so there’s nothing to draft.</p>',
                    unsafe_allow_html=True,
                )

            if st.session_state.get("generation_complete", False):
                # The scanned source copy is deleted once generation finishes,
                # so a finished scan links to its docs instead of generating again.
                if st.button("View documentation", key="cta_scan_view_docs", type="primary"):
                    st.session_state["current_screen"] = "docs"
                    st.rerun()
            elif st.button("Generate documentation", key="cta_generate_docs", type="primary"):
                st.session_state["generation_attempt"] = 0
                st.session_state["generation_complete"] = False
                st.session_state["qa_chat_history"] = []
                st.session_state["current_screen"] = "generation"
                st.rerun()
