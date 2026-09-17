"""
screens/docs.py -- CodeDocAI
Renders the dynamically generated AI documentation and module overviews.
"""

import sys
import json
import os
from pathlib import Path
import streamlit as st

_ROOT_DIR = Path(__file__).resolve().parents[2]
if str(_ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(_ROOT_DIR))

# Match the exact absolute path from pipeline.py
_CACHE_PATH = _ROOT_DIR / "docs_cache.json"

from helpers import render_nav_rail

def render_documentation() -> None:
    if st.session_state.get("current_screen") != "docs":
        return

    render_nav_rail("docs")

    st.markdown('<div class="section-label">GENERATED DOCUMENTATION</div>', unsafe_allow_html=True)
    
    pipeline_data = st.session_state.get("pipeline_results")
    
    # BULLETPROOF CACHE: Fallback to the disk cache and re-hydrate session state
    if not pipeline_data and _CACHE_PATH.exists():
        try:
            with open(_CACHE_PATH, "r", encoding="utf-8") as f:
                pipeline_data = json.load(f)
            # Re-hydrate the state so it persists in the main thread now
            st.session_state["pipeline_results"] = pipeline_data
        except Exception:
            pass

    if not pipeline_data:
        st.warning("No documentation found. Please run a scan first.")
        return

    # 1. Render the Architectural Overview
    st.markdown(pipeline_data.get("overview", "No architecture overview generated."))
    st.markdown("---")

    # 2. Render the Functions & Docstrings
    functions = pipeline_data.get("functions", [])
    files_dict = {}
    
    for fn in functions:
        fpath = fn.get("file", "unknown")
        if fpath not in files_dict:
            files_dict[fpath] = []
        files_dict[fpath].append(fn)

    for file_path, funcs in files_dict.items():
        st.markdown(f"### `{file_path}`")
        for fn in funcs:
            badge = " 🤖 AI DRAFT" if fn.get("is_ai_draft") else ""
            with st.expander(f"Function: {fn.get('name', 'unknown')}() {badge}"):
                st.markdown(f"**Docstring:**\n```python\n{fn.get('docstring', '')}\n```")
                st.markdown(f"**Source:**\n```python\n{fn.get('source', '')}\n```")
        st.markdown("---")

    # Navigation Buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("← NEW SCAN"):
            st.session_state["current_screen"] = "scan"
            st.rerun()
    with col3:
        if st.button("ASK A QUESTION →"):
            st.session_state["current_screen"] = "qa"
            st.rerun()