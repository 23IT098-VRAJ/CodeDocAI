"""
screens/scan.py -- CodeDocAI
Scan screen renderer with Tabbed UI and Live Backend Streaming.
"""

import math as _math
import os
import sys
import tempfile
from pathlib import Path

import streamlit as st

# Ensure project root is in sys.path so backend is accessible
_ROOT_DIR = str(Path(__file__).resolve().parents[2])
if _ROOT_DIR not in sys.path:
    sys.path.insert(0, _ROOT_DIR)

try:
    from helpers import render_nav_rail, _reset_to_new_scan
except ImportError:
    from app.helpers import render_nav_rail, _reset_to_new_scan

from backend.repo.loader import extract_zip, clone_github_repo, RepoValidationError
from backend.pipeline import run_pipeline
from backend.parser.extractor import extract_functions


def render_scan() -> None:
    # -- Prevent Ghosting --
    if st.session_state.get("current_screen", "scan") != "scan":
        return

    # Shared Top Navigation Rail
    render_nav_rail("scan")

    status = st.session_state.get("scan_status", "idle")

    # =====================================================================
    # INPUT STATE
    # =====================================================================
    if status != "populated":
        st.markdown(
            '<div class="section-label">PROVIDE YOUR CODE</div>'
            '<p class="scan-intro">Select your repository source below.</p>'
            '<div class="scan-parameters" style="margin-bottom: 20px;"><span style="color: var(--accent-amber); font-weight: 500;">TARGET PARAMETERS:</span> .py files only &middot; Max 100MB / 500 files per scan</div>',
            unsafe_allow_html=True,
        )

        github_url = st.text_input(
            "GITHUB REPOSITORY URL",
            placeholder="https://github.com/username/repository",
            key="scan_github_url_input",
            label_visibility="collapsed"
        )
        st.markdown(
            '<div class="scan-microcopy" style="margin-top: 10px;">'
            '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--accent-amber)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink: 0; margin-top: 2px;"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>'
            '<span><span style="color: var(--text-primary); font-weight: 500;">Requires root HTTPS URL.</span> For private repositories, use the .ZIP upload below.</span>'
            '</div>',
            unsafe_allow_html=True,
        )

        # Visual OR Divider
        st.markdown(
            '<div class="scan-or-divider">'
            '<div class="scan-or-line"></div>'
            '<div class="scan-or-label">OR UPLOAD .ZIP</div>'
            '<div class="scan-or-line"></div>'
            '</div>',
            unsafe_allow_html=True
        )

        uploaded_file = st.file_uploader(
            label="Upload project (.zip)",
            type=["zip"],
            key="scan_file_upload",
            label_visibility="collapsed"
        )

        # Pipeline Preview
        st.markdown(
            '<div class="scan-preview-row" style="margin-top: 30px;">'
            '<div class="scan-preview-step"><span style="color: var(--text-primary);">[01]</span> INGEST REPOSITORY</div>'
            '<div class="scan-preview-arrow">→</div>'
            '<div class="scan-preview-step"><span style="color: var(--text-primary);">[02]</span> AST ISOLATION</div>'
            '<div class="scan-preview-arrow">→</div>'
            '<div class="scan-preview-step"><span style="color: var(--text-primary);">[03]</span> FLAG MISSING SIGNATURES</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown('<div id="cta-generate-marker"></div>', unsafe_allow_html=True)
        
        # --- ERROR DISPLAY MOVED HERE ---
        if status == "error":
            err_msg = st.session_state.get("scan_error_message", "An error occurred.")
            st.markdown(f'<p class="scan-error-line" style="margin-bottom: 16px;">{err_msg}</p>', unsafe_allow_html=True)
            
        # Trigger Backend Pipeline
        if st.button("SCAN REPOSITORY", key="cta_scan_repo"):
            has_zip = uploaded_file is not None
            has_url = bool(github_url and github_url.strip())

            if not has_zip and not has_url:
                st.session_state["scan_status"] = "error"
                st.session_state["scan_error_message"] = "Please provide a GitHub URL or upload a .ZIP file."
                st.rerun()

            temp_dir = tempfile.mkdtemp(prefix="codedocai_scan_")
            repo_source = None

            try:
                with st.status("Processing Repository...", expanded=True) as status_box:
                    # 1. Loading Phase
                    if has_zip:
                        status_box.write(f"📦 Extracting `{uploaded_file.name}`...")
                        uploaded_file.seek(0)
                        repo_source = extract_zip(uploaded_file, temp_dir)
                        st.session_state["scan_github_url"] = uploaded_file.name
                    else:
                        clean_url = github_url.strip()
                        status_box.write(f"🐙 Cloning `{clean_url}`...")
                        repo_source = clone_github_repo(clean_url, temp_dir)
                        st.session_state["scan_github_url"] = clean_url

                    st.session_state["repo_source"] = repo_source

                    local_path = repo_source.get("local_path", "")
                    py_files = repo_source.get("py_files", [])

                    # Pre-calculate file function totals so the ledger renders correctly
                    file_stats = {}
                    func_to_file = {}
                    for rel_p in py_files:
                        norm_p = rel_p.replace("\\", "/")
                        abs_p = os.path.join(local_path, rel_p)
                        file_stats[norm_p] = {"path": norm_p, "functions": 0, "missing": 0}
                        try:
                            with open(abs_p, "r", encoding="utf-8", errors="ignore") as f:
                                content = f.read()
                            funcs = extract_functions(content, rel_p)
                            file_stats[norm_p]["functions"] = len(funcs)
                            for fn in funcs:
                                func_to_file.setdefault(fn["name"], []).append(norm_p)
                        except Exception:
                            pass

                    current_file = py_files[0].replace("\\", "/") if py_files else None

                    # 2. Streaming Phase
                    for event in run_pipeline(repo_source):
                        ev_type = event.get("type")

                        if ev_type == "progress":
                            fn_or_file = event.get("function", "")
                            status_txt = event.get("status", "")
                            if status_txt == "parsing":
                                current_file = fn_or_file.replace("\\", "/")
                                status_box.write(f"🔍 Parsing: `{current_file}`")
                            elif status_txt == "summarizing":
                                status_box.write(f"⚡ Summarizing: `{fn_or_file}`")
                            else:
                                status_box.write(f"⚙️ {status_txt.capitalize()}: {fn_or_file}")

                        elif ev_type == "result":
                            fn_name = event.get("function", "")
                            docstring = event.get("docstring", "")
                            is_missing = (docstring != "(Original docstring retained)")

                            target_file = None
                            if fn_name in func_to_file and func_to_file[fn_name]:
                                target_file = func_to_file[fn_name].pop(0)
                            elif current_file:
                                target_file = current_file

                            if target_file and target_file in file_stats:
                                if is_missing:
                                    file_stats[target_file]["missing"] += 1

                        elif ev_type == "error":
                            st.session_state["scan_status"] = "error"
                            st.session_state["scan_error_message"] = event.get("message", "Pipeline failed.")
                            status_box.update(label="Scan failed", state="error")
                            st.rerun()

                        elif ev_type == "done":
                            # Compile final ledger list
                            ledger_results = [stats for stats in file_stats.values() if stats["functions"] > 0]
                            file_count = len(ledger_results)
                            missing_count = sum(r["missing"] for r in ledger_results)

                            st.session_state["scan_results"] = ledger_results
                            st.session_state["scan_summary"] = {
                                "file_count": file_count,
                                "missing_count": missing_count,
                            }
                            st.session_state["scan_status"] = "populated"
                            st.session_state["scan_error_message"] = None
                            st.session_state["repo_overview"] = event.get("overview", "")
                            status_box.update(label="Repository scan complete!", state="complete", expanded=False)
                            st.rerun()

            except RepoValidationError as e:
                st.session_state["scan_status"] = "error"
                st.session_state["scan_error_message"] = str(e)
                st.rerun()
            except Exception as e:
                st.session_state["scan_status"] = "error"
                st.session_state["scan_error_message"] = f"Repository scan failed: {str(e)}"
                st.rerun()

        # Security Assurance Tag
        st.markdown(
            '<div class="scan-security-tag">'
            '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#4CAF50" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink: 0;"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>'
            '<span><span style="color: #4CAF50; font-weight: 500;">SESSION ISOLATED:</span> Source files are processed in memory and immediately discarded. Zero disk retention.</span>'
            '</div>',
            unsafe_allow_html=True,
        )

    # =====================================================================
    # RESULTS STATE
    # =====================================================================
    else:
        st.markdown('<div class="section-label">SOURCE CODE</div>', unsafe_allow_html=True)

        source_name = "Uploaded .zip archive"
        if st.session_state.get("scan_github_url", "").strip():
            source_name = st.session_state.get("scan_github_url", "").strip()

        st.markdown(
            f'<div style="display: flex; align-items: center; gap: 16px; margin-bottom: var(--space-4);">'
            f'<span style="font-family: \'IBM Plex Mono\', monospace; font-size: 0.85rem; color: var(--text-primary);">{source_name}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

        st.markdown('<div id="cta-secondary-marker"></div>', unsafe_allow_html=True)
        if st.button("NEW SCAN", key="cta_scan_reset"):
            st.session_state["repo_source"] = None
            st.session_state["repo_overview"] = None
            try:
                from helpers import _reset_to_new_scan
            except ImportError:
                from app.helpers import _reset_to_new_scan
            _reset_to_new_scan()

        results = st.session_state.get("scan_results", [])

        # Removed redundant error display from here. 
        # Only rendering the success ledger:
        if status == "populated" and results is not None:
            summary = st.session_state.get("scan_summary") or {}
            file_count = summary.get("file_count", len(results))
            missing_count = summary.get("missing_count", 0)

            if missing_count > 0:
                summary_text = f'{file_count} files scanned\u2009\u00B7\u2009{missing_count} functions missing docstrings'
            else:
                summary_text = f'{file_count} files scanned\u2009\u00B7\u2009fully documented'

            ledger_html = (
                '<div id="ghost-scan-results" class="scan-results-section">'
                '<div class="section-label">SCAN RESULTS</div>'
                f'<p class="scan-summary">{summary_text}</p>'
            )

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
                    meta_text = f'{funcs} functions\u2009\u00B7\u2009{missing} missing docstrings'
                else:
                    meta_class = "ledger-meta-clean"
                    meta_text = f'{funcs} functions\u2009\u00B7\u2009fully documented'
                
                ledger_html += (
                    f'<div class="ledger-row">'
                    f'<div class="ledger-index"><span class="severity-pip {pip_color}"></span>{idx_str}</div>'
                    f'<span class="ledger-path">{path}</span>'
                    f'<span class="{meta_class}">{meta_text}</span>'
                    f'</div>'
                )
            ledger_html += '</div>'
            st.markdown(ledger_html, unsafe_allow_html=True)

            if missing_count > 0:
                est_minutes = max(1, _math.ceil(missing_count / 10))
                plural = "s" if missing_count != 1 else ""
                est_html = (
                    '<div id="ghost-scan-estimate" class="scan-estimate-section">'
                    '<div class="section-label">ESTIMATED GENERATION TIME</div>'
                    f'<p class="scan-estimate-body">{missing_count} draft{plural} to generate \u00B7 '
                    f'~{est_minutes} min (constrained by ML processing time)</p>'
                    '</div>'
                )
                st.markdown(est_html, unsafe_allow_html=True)
            else:
                st.markdown(
                    '<div id="ghost-scan-estimate"><p class="scan-estimate-clean">Every file is already documented \u2014 nothing to draft.</p></div>',
                    unsafe_allow_html=True,
                )

            st.markdown(
                '<div class="system-note">SYSTEM NOTE: AST parser automatically bypassed __init__.py, test directories, and standard library imports.</div>',
                unsafe_allow_html=True,
            )

            st.markdown('<div id="cta-generate-marker"></div>', unsafe_allow_html=True)
            if st.button("GENERATE DOCUMENTATION", key="cta_generate_docs"):
                st.session_state["generation_attempt"] = 0
                st.session_state["generation_complete"] = False
                st.session_state["qa_chat_history"] = []
                st.session_state["current_screen"] = "generation"
                st.rerun()