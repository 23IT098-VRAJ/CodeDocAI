"""
screens/export.py -- CodeDocAI
Export screen renderer (Session 7).
Generates an in-memory ZIP (no filesystem I/O) containing:
  documentation.md, qa_transcript.md, metadata.json
"""

import datetime as _datetime
import io as _io
import json as _json
import zipfile as _zipfile

import streamlit as st

from backend.coverage import coverage_markdown
from components.diff_view import render_patch
from helpers import _build_docs_markdown, audit_event, new_scan_button, page_heading, queue_toast, render_stats


def _audit_export() -> None:
    audit_event("EXPORT", "Downloaded the documentation archive (codedocai_export.zip).")
    queue_toast("Export downloaded: codedocai_export.zip", ":material/download_done:")


def add_documented_outputs(zf, pipeline_results: dict) -> None:
    """
    Adds what the pipeline produced locally to the export archive: the coverage
    report, the docstring patch, and a documented copy of every file that gained
    a docstring. Results saved by an older version have none of these.
    """
    coverage = pipeline_results.get("coverage") or {}
    if coverage:
        zf.writestr("coverage_report.md", coverage_markdown(coverage))
    if pipeline_results.get("patch"):
        zf.writestr("docstrings.patch", pipeline_results["patch"])
    for rel_path, documented_source in (pipeline_results.get("documented_files") or {}).items():
        zf.writestr(f"documented_source/{rel_path}", documented_source)


def render_export() -> None:
    page_heading("Export")

    generation_complete = st.session_state.get("generation_complete", False)

    # ------------------------------------------------------------------
    # EMPTY STATE -- generation not yet complete
    # ------------------------------------------------------------------
    if not generation_complete:
        st.markdown(
            '<div class="docs-empty-head">There’s nothing to export yet.</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p class="docs-empty-sub">Run a scan and generate documentation first.</p>',
            unsafe_allow_html=True,
        )
        return

    # ------------------------------------------------------------------
    # POPULATED STATE -- compute stats and render download
    # ------------------------------------------------------------------
    scan_summary     = st.session_state.get("scan_summary") or {}
    scan_results     = st.session_state.get("scan_results") or []
    qa_chat_history  = st.session_state.get("qa_chat_history", [])

    files_scanned        = scan_summary.get("file_count", len(scan_results))
    coverage = (st.session_state.get("pipeline_results") or {}).get("coverage") or {}
    # Counts what was actually drafted; older results without coverage fall back to the scan estimate.
    functions_documented = coverage.get("docstrings_drafted", scan_summary.get("missing_count", 0))
    questions_asked      = len([m for m in qa_chat_history if m.get("role") == "user"])

    q_label = "Question asked" if questions_asked == 1 else "Questions asked"

    stats = [("Files scanned", files_scanned), ("Docstrings drafted", functions_documented), (q_label, questions_asked)]
    if coverage.get("functions_after_pct") is not None:
        stats.append(("Functions documented", f"{coverage['functions_after_pct']}%"))
    render_stats(stats, key="export_stats")

    st.markdown(
        '<div class="archive-manifest">'
        'codedocai_export.zip/\n'
        '├── documentation.md      overview and docstrings\n'
        '├── qa_transcript.md      Q&amp;A with citations\n'
        '├── metadata.json         models, totals, timestamps\n'
        '├── coverage_report.md    before and after, per file\n'
        '├── docstrings.patch      ready for git apply\n'
        '└── documented_source/    your files, docstrings written in'
        '</div>',
        unsafe_allow_html=True
    )

    # ------------------------------------------------------------------
    # Build in-memory ZIP (no filesystem I/O)
    # ------------------------------------------------------------------
    pipeline_results = st.session_state.get("pipeline_results") or {}
    doc_md = _build_docs_markdown(pipeline_results, scan_summary)

    transcript_lines = ["# CodeDocAI Q&A Transcript", ""]
    for i in range(0, len(qa_chat_history), 2):
        user_msg = qa_chat_history[i] if i < len(qa_chat_history) else None
        asst_msg = qa_chat_history[i + 1] if i + 1 < len(qa_chat_history) else None
        if user_msg:
            transcript_lines.append(f"**Q:** {user_msg.get('content', '')}")
            transcript_lines.append("")
        if asst_msg:
            transcript_lines.append(f"**A:** {asst_msg.get('content', '')}")
            citation = asst_msg.get("citation")
            if citation:
                transcript_lines.append("")
                transcript_lines.append(f"*Citation: {citation}*")
            transcript_lines.append("")
            transcript_lines.append("---")
            transcript_lines.append("")
    qa_md = "\n".join(transcript_lines)

    metadata = {
        "project": "CodeDocAI",
        "export_timestamp": _datetime.datetime.now(_datetime.timezone.utc).isoformat(),
        "pipeline_telemetry": {
            "model_draft": "CodeT5-small (fine-tuned)",
            "orchestration": "CrewAI",
            "vector_store": "ChromaDB",
            "qa_model": "Gemini API (RAG)",
        },
        "session_stats": {
            "files_scanned": files_scanned,
            "functions_documented": functions_documented,
            "questions_asked": questions_asked,
        },
        "coverage": {key: value for key, value in coverage.items() if key != "files"},
    }
    metadata_json = _json.dumps(metadata, indent=2)

    zip_buffer = _io.BytesIO()
    with _zipfile.ZipFile(zip_buffer, mode="w", compression=_zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("documentation.md", doc_md)
        zf.writestr("qa_transcript.md", qa_md)
        zf.writestr("metadata.json", metadata_json)
        add_documented_outputs(zf, pipeline_results)
    zip_bytes = zip_buffer.getvalue()

    patch_text = pipeline_results.get("patch") or ""
    if patch_text:
        st.markdown('<h2 class="section-h2">Patch preview</h2>', unsafe_allow_html=True)
        render_patch(patch_text, title="docstrings.patch", key="export_patch", max_height=420)

    with st.container(horizontal=True, gap="small", vertical_alignment="center", key="export_actions"):
        st.download_button(
            label="Export .zip",
            data=zip_bytes,
            file_name="codedocai_export.zip",
            mime="application/zip",
            key="cta_export_download",
            on_click=_audit_export,
            type="primary",
            icon=":material/download:",
        )
        # Clears the session completely, after asking for confirmation
        new_scan_button("New scan", key="export_new_scan", type="tertiary", icon=":material/refresh:")
