"""
screens/qa.py -- CodeDocAI
Q&A screen renderer (Phase 8.5 Real RAG Integration).
"""

import html as _html
import re as _re
import streamlit as st

try:
    from helpers import render_nav_rail, _reset_to_new_scan
except ImportError:
    from app.helpers import render_nav_rail, _reset_to_new_scan

from backend.rag.vectorstore import query_similar
from backend.agents.qa import answer_codebase_question


def _process_and_append_qa(question: str):
    """Helper to run RAG + CrewAI and append to session state, used by both chips and text input."""
    with st.spinner("Querying ChromaDB vector store and synthesizing response..."):
        # 1. Retrieve RAG context
        try:
            retrieved_chunks = query_similar(question, n_results=3)
            context_block = "\n---\n".join(retrieved_chunks) if retrieved_chunks else "No direct matches found in vectorstore."
        except Exception as e:
            context_block = f"Error retrieving context: {e}"

        # 2. Ask CrewAI
        try:
            ans_dict = answer_codebase_question(question, context_block)
            answer_text = ans_dict.get("answer", "No answer generated.")
            citations = ans_dict.get("citations", [])
        except Exception as e:
            answer_text = f"⚠️ Unable to generate answer due to API cooldown or network interruption ({e}). Please try again in 2 minutes."
            citations = []
        
        # 3. Defensive Citation Formatting (handles both dict and str items)
        cit_text = ""
        if citations:
            cit_parts = []
            for c in citations:
                if isinstance(c, dict):
                    func = c.get("function", "")
                    file = c.get("file", "")
                    if func and file:
                        cit_parts.append(f"{file}::{func}()")
                    elif file:
                        cit_parts.append(f"{file}")
                    elif func:
                        cit_parts.append(f"{func}()")
                elif isinstance(c, str) and c.strip():
                    cit_parts.append(c.strip())
            cit_text = " | ".join(cit_parts)

        # 4. Save to chat history
        st.session_state["qa_chat_history"].append({"role": "user", "content": question})
        st.session_state["qa_chat_history"].append({
            "role": "assistant",
            "content": answer_text,
            "citation": cit_text if cit_text else None,
        })


def render_qa() -> None:
    render_nav_rail("qa")

    scan_results = st.session_state.get("scan_results")
    qa_chat_history = st.session_state.get("qa_chat_history", [])

    if scan_results is None:
        st.markdown(
            '<div class="docs-empty-head">No codebase to ask about yet.</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p class="docs-empty-sub">Initialize a scan to build the vector index.</p>',
            unsafe_allow_html=True,
        )
        return

    st.markdown('<div class="section-label">ASK THE CODEBASE</div>', unsafe_allow_html=True)

    if not qa_chat_history:
        st.markdown(
            '<p class="qa-intro">'
            'Ask anything about this codebase \u2014 answers are grounded in the code '
            'itself, with a citation back to the source.'
            '</p>',
            unsafe_allow_html=True,
        )

        total_funcs = sum(row.get("functions", row.get("missing", 0)) for row in scan_results)
        total_files = len(scan_results)

        st.markdown(
            f'<div class="vector-status-bar"><span class="vector-active-dot">●</span> [ChromaDB Active] &middot; Vectorized {total_funcs} functions across {total_files} files.</div>',
            unsafe_allow_html=True
        )

        example_queries = [
            "How does the AST parser handle nested definitions?",
            "What model fine-tuning parameters are used?",
            "Where is the ChromaDB embedding initialized?",
        ]

        chip_cols = st.columns(len(example_queries), gap="small")
        for i, q_text in enumerate(example_queries):
            chip_key = f"qa_chip_{i+1}"
            with chip_cols[i]:
                st.markdown('<div class="qa-chip-marker"></div>', unsafe_allow_html=True)
                if st.button(f"{q_text}\u00A0\u2192", key=chip_key, use_container_width=True):
                    _process_and_append_qa(q_text)
                    st.rerun()

    else:
        transcript_html = '<div class="qa-transcript">'
        for i in range(0, len(qa_chat_history), 2):
            user_msg = qa_chat_history[i] if i < len(qa_chat_history) else None
            asst_msg = qa_chat_history[i + 1] if i + 1 < len(qa_chat_history) else None

            if user_msg:
                q_text = _html.escape(user_msg.get("content", ""))
                transcript_html += (
                    f'<div class="qa-turn">'
                    f'<div class="qa-q-row">'
                    f'<span class="qa-turn-label qa-q-label">Q</span>'
                    f'<div class="qa-q-text">{q_text}</div>'
                    f'</div>'
                )

                if asst_msg:
                    raw_content = asst_msg.get("content", "")
                    a_text = _html.escape(raw_content)
                    
                    # Regex replacement opens AND closes HTML tags correctly
                    a_text = _re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', a_text)
                    a_text = _re.sub(r'`(.*?)`', r'<code>\1</code>', a_text)
                    
                    citation = asst_msg.get("citation")
                    citation_html = ""
                    fallback_class = ""
                    if citation:
                        cit_esc = _html.escape(citation)
                        citation_html = f'<div class="qa-citation-pill">{cit_esc}</div>'
                    else:
                        fallback_class = " qa-a-fallback"

                    transcript_html += (
                        f'<div class="qa-a-row">'
                        f'<span class="qa-turn-label qa-a-label">A</span>'
                        f'<div class="qa-a-body">'
                        f'<div class="qa-a-text{fallback_class}">{a_text}</div>'
                        f'{citation_html}'
                        f'</div>'
                        f'</div>'
                    )

                transcript_html += '</div>'

        transcript_html += '</div>'
        st.markdown(transcript_html, unsafe_allow_html=True)

    # ------------------------------------------------------------------
    # Query Input Row
    # ------------------------------------------------------------------
    st.markdown('<div class="qa-ask-wrap">', unsafe_allow_html=True)
    with st.form(key="qa_ask_form", clear_on_submit=True):
        col_input, col_submit = st.columns([5, 1], gap="medium", vertical_alignment="bottom")
        with col_input:
            user_input = st.text_input(
                label="Ask a question about this codebase",
                placeholder='Query the codebase (e.g., "Where is the AST parsed?")...',
                key="qa_input",
                label_visibility="collapsed",
                autocomplete="off",
            )
        with col_submit:
            submit_clicked = st.form_submit_button("ASK", use_container_width=True)

        if submit_clicked:
            clean_q = user_input.replace("\u00A0\u2192", "").replace(" \u2192", "").replace(" →", "").strip()
            if clean_q:
                _process_and_append_qa(clean_q)
                st.rerun()
                
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="qa-disclaimer">Responses are constrained strictly to the ingested AST and generated docstrings. Context limits apply.</div>',
        unsafe_allow_html=True,
    )

    # -- Unified Reset Action --
    st.markdown('<div style="height: 16px;"></div>', unsafe_allow_html=True) 
    _, col_reset, _ = st.columns([3, 2, 3])
    with col_reset:
        if st.button("← START NEW SCAN", key="qa_new_scan_bottom", type="secondary", use_container_width=True):
            _reset_to_new_scan()