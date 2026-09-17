"""
screens/export.py -- CodeDocAI
Export screen renderer (Session 7).
Generates an in-memory ZIP (no filesystem I/O) containing:
  documentation.md, qa_transcript.md, metadata.json
"""

import io as _io
import json as _json
import zipfile as _zipfile
import datetime as _datetime

import streamlit as st

try:
    from helpers import render_nav_rail, _build_docs_markdown, _reset_to_new_scan
except ImportError:
    from app.helpers import render_nav_rail, _build_docs_markdown, _reset_to_new_scan


def render_export() -> None:
    render_nav_rail("export")

    st.markdown(
        '<div class="section-label">PROJECT EXPORT</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="gen-intro">Archive generated documentation, chat transcripts, '
        'and execution metadata.</p>',
        unsafe_allow_html=True,
    )

    generation_complete = st.session_state.get("generation_complete", False)

    # ------------------------------------------------------------------
    # EMPTY STATE -- generation not yet complete
    # ------------------------------------------------------------------
    if not generation_complete:
        st.markdown(
            '<div class="docs-empty-head">No documentation has been generated yet.</div>',
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
    functions_documented = scan_summary.get("missing_count", 0)
    questions_asked      = len([m for m in qa_chat_history if m.get("role") == "user"])

    # Dynamic Pluralization Check
    q_label = "QUESTION ASKED" if questions_asked == 1 else "QUESTIONS ASKED"

    # Stats grid
    stats_html = (
        '<div class="export-stats-grid">'
        f'<div class="export-stat">'
        f'<span class="export-stat-value">{files_scanned}</span>'
        f'<span class="export-stat-label">FILES SCANNED</span>'
        f'</div>'
        f'<div class="export-stat">'
        f'<span class="export-stat-value">{functions_documented}</span>'
        f'<span class="export-stat-label">FUNCTIONS DOCUMENTED</span>'
        f'</div>'
        f'<div class="export-stat">'
        f'<span class="export-stat-value">{questions_asked}</span>'
        f'<span class="export-stat-label">{q_label}</span>'
        f'</div>'
        '</div>'
    )
    st.markdown(stats_html, unsafe_allow_html=True)

    # Inject the File Tree Manifest directly below the stats grid
    st.markdown(
        '<div class="archive-manifest">'
        'codedocai_export.zip/\n'
        '├── documentation.md      (Generated module overviews & docstrings)\n'
        '├── qa_transcript.md      (Complete Q&A session log with citations)\n'
        '└── metadata.json         (Pipeline telemetry & execution timestamps)'
        '</div>',
        unsafe_allow_html=True
    )

    # ------------------------------------------------------------------
    # Build in-memory ZIP (no filesystem I/O)
    # ------------------------------------------------------------------
    # File 1: documentation.md
    doc_md = _build_docs_markdown(scan_results, scan_summary)

    # File 2: qa_transcript.md
    transcript_lines = ["# CodeDocAI \u2014 Q&A Transcript", ""]
    for i in range(0, len(qa_chat_history), 2):
        user_msg = qa_chat_history[i] if i < len(qa_chat_history) else None
        asst_msg = qa_chat_history[i + 1] if i + 1 < len(qa_chat_history) else None
        if user_msg:
            transcript_lines.append(f"**Q:** {user_msg.get('content', '')}")  # noqa: E501
            transcript_lines.append("")
        if asst_msg:
            transcript_lines.append(f"**A:** {asst_msg.get('content', '')}")
            citation = asst_msg.get("citation")
            if citation:
                transcript_lines.append(f"")
                transcript_lines.append(f"*Citation: {citation}*")
            transcript_lines.append("")
            transcript_lines.append("---")
            transcript_lines.append("")
    qa_md = "\n".join(transcript_lines)

    # File 3: metadata.json
    metadata = {
        "project": "CodeDocAI",
        "export_timestamp": _datetime.datetime.utcnow().isoformat() + "Z",
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
    }
    metadata_json = _json.dumps(metadata, indent=2)

    # Write ZIP to BytesIO buffer -- no filesystem I/O
    zip_buffer = _io.BytesIO()
    with _zipfile.ZipFile(zip_buffer, mode="w", compression=_zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("documentation.md", doc_md)
        zf.writestr("qa_transcript.md", qa_md)
        zf.writestr("metadata.json", metadata_json)
    zip_bytes = zip_buffer.getvalue()  # must call after ZipFile is closed

    # Tight button grouping
    col_export, col_scan, _ = st.columns([1.5, 1.5, 4])  # Keeps them clustered on the left

    with col_export:
        st.download_button(
            label="EXPORT .ZIP",
            data=zip_bytes,
            file_name="codedocai_export.zip",
            mime="application/zip",
            key="cta_export_download",
            use_container_width=True,
        )

    with col_scan:
        if st.button("NEW SCAN", key="export_new_scan", type="secondary", use_container_width=True):
            st.session_state["current_screen"] = "scan"
            st.rerun()

    # Session Lifecycle Disclaimer
    st.markdown(
        '<div class="session-disclaimer">SESSION STATE: Downloading this archive does not terminate the session. Click \'New Scan\' to safely purge all memory and vector embeddings.</div>',
        unsafe_allow_html=True
    )
