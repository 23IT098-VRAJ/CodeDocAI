"""
screens/qa.py -- CodeDocAI
Q&A screen renderer (Phase 8.5 Real RAG Integration).
"""

import contextlib as _contextlib
import html as _html
import logging
import re as _re

import streamlit as st

from backend.agents.qa import GREETING_REPLY, answer_codebase_question, is_follow_up, retrieval_query
from backend.rag.vectorstore import query_chunks
from backend.security import SECURITY_REFUSAL, classify_question
from helpers import (
    audit_event,
    new_scan_button,
    page_heading,
    session_collection_name,
)

logger = logging.getLogger(__name__)


def _cache_key(question: str) -> str:
    """Same question, whatever its casing, punctuation or spacing."""
    return " ".join(_re.sub(r"[^\w\s]", " ", question.lower()).split())


def _audit_question(question: str) -> None:
    """Records the question for the signed-in developer, rated by the local classifier."""
    severity = classify_question(question)
    blocked = " [blocked before reaching the model]" if severity == "CRITICAL" else ""
    audit_event("Q&A_QUERY", f"Asked AI: '{question}'{blocked}", severity=severity)


def _append_turn(question: str, answer: str, citation: str | None = None) -> None:
    st.session_state["qa_chat_history"].append({"role": "user", "content": question})
    st.session_state["qa_chat_history"].append({"role": "assistant", "content": answer, "citation": citation})


def _process_and_append_qa(question: str):
    """Helper to run RAG + CrewAI and append to session state, used by both chips and text input."""

    # --- FAST-PATH INTERCEPTOR (Saves API calls & prevents Context Forcing) ---
    # Strip punctuation for clean matching (e.g., "Who are you!" -> "who are you")
    clean_intent = _re.sub(r'[^a-zA-Z\s]', '', question.lower().strip())
    greeting_intents = ["who are you", "what are you", "hello", "hi", "hey", "greetings"]

    if clean_intent in greeting_intents or clean_intent.startswith(("hi ", "hello ")):
        _append_turn(question, GREETING_REPLY)
        return  # Instantly halt execution. Do not query ChromaDB. Do not query the LLM.
    # --------------------------------------------------------------------------

    # --- SECURITY INTERCEPTOR (refused locally: no retrieval, no API call) ---
    # Requests for credentials or environment values, and attempts to override the
    # assistant's instructions, never leave this machine.
    if classify_question(question) == "CRITICAL":
        _append_turn(question, SECURITY_REFUSAL)
        return

    # --- ANSWER CACHE (a repeated question costs no API call) ---
    # A follow-up ("and the second one?") means something different after each question,
    # so its cache entry is keyed on the question before it as well.
    history = list(st.session_state.get("qa_chat_history") or [])
    cache_key = _cache_key(retrieval_query(question, history) if is_follow_up(question, history) else question)
    cached = st.session_state.setdefault("qa_answer_cache", {}).get(cache_key)
    if cached:
        _append_turn(question, cached["content"], cached["citation"])
        return

    answered = False
    with _contextlib.nullcontext():  # the caller shows progress in a compact status
        # 1. Retrieve RAG context
        try:
            retrieved_chunks = query_chunks(
                retrieval_query(question, history), n_results=4, collection_name=session_collection_name()
            )
        except Exception as e:  # noqa: BLE001 - the model can still answer without retrieved code
            logger.warning("Vector retrieval failed: %s", e)
            retrieved_chunks = []

        # 2. Ask CrewAI
        try:
            ans_dict = answer_codebase_question(question, retrieved_chunks, history)
            answer_text = ans_dict.get("answer", "The model returned an empty answer.")
            citations = ans_dict.get("citations", [])
            answered = True
        except Exception as e:  # noqa: BLE001 - shown in the chat as the reply
            answer_text = f"No answer this time: {e} Try again in a couple of minutes."
            citations = []

        # 3. Defensive Citation Formatting
        cit_text = ""
        if citations:
            cit_parts = []
            for c in citations:
                if isinstance(c, dict):
                    if c.get("kind") == "overview":
                        cit_parts.append("Repository overview")
                        continue
                    func = c.get("function", "")
                    file = c.get("file", "")
                    call = "" if c.get("kind") == "class" else "()"
                    if func and file:
                        cit_parts.append(f"{file}::{func}{call}")
                    elif file:
                        cit_parts.append(f"{file}")
                    elif func:
                        cit_parts.append(f"{func}{call}")
                elif isinstance(c, str) and c.strip():
                    cit_parts.append(c.strip())
            cit_text = " | ".join(cit_parts)

        # 4. Save to chat history
        _append_turn(question, answer_text, cit_text if cit_text else None)

        # Only real answers are cached; an API failure should be retried next time.
        if answered:
            st.session_state["qa_answer_cache"][cache_key] = {
                "content": answer_text,
                "citation": cit_text if cit_text else None,
            }


USER_AVATAR = ":material/person:"
ASSISTANT_AVATAR = ":material/data_object:"


def _citation_pills(citation: str | None) -> str:
    if not citation:
        return ""
    pills = "".join(
        f'<span class="qa-citation-pill">{_html.escape(part.strip())}</span>'
        for part in citation.split("|") if part.strip()
    )
    return f'<div class="qa-citations" aria-label="Sources">{pills}</div>'


def _render_answer(content: str, citation: str | None) -> None:
    st.markdown(content)
    pills = _citation_pills(citation)
    if pills:
        st.markdown(pills, unsafe_allow_html=True)


def _render_history(history: list) -> None:
    for message in history:
        if message.get("role") == "user":
            with st.chat_message("user", avatar=USER_AVATAR):
                st.text(message.get("content", ""))
        else:
            with st.chat_message("assistant", avatar=ASSISTANT_AVATAR):
                _render_answer(message.get("content", ""), message.get("citation"))


def _starter_questions(scan_results: list) -> list[str]:
    largest_file = max(scan_results, key=lambda row: row.get("functions", 0)).get("path") if scan_results else None
    questions = ["What is this project about?"]
    if largest_file:
        questions.append(f"What does {largest_file} do?")
    return questions


def render_qa() -> None:
    scan_results = st.session_state.get("scan_results")
    history = st.session_state.get("qa_chat_history", [])

    if scan_results is None:
        page_heading("Ask the codebase")
        st.markdown('<p class="docs-empty-sub">Scan a repository and generate its documentation first.</p>',
                    unsafe_allow_html=True)
        if st.button("Start a scan", key="qa_empty_scan", type="primary"):
            st.session_state["current_screen"] = "scan"
            st.rerun()
        return

    total_funcs = sum(row.get("functions", row.get("missing", 0)) for row in scan_results)
    page_heading("Ask the codebase")
    with st.container(horizontal=True, vertical_alignment="center", gap="small", key="qa_meta"):
        st.markdown(
            f'<span class="vector-status-bar"><span class="vector-active-dot" aria-hidden="true">●</span>'
            f'{total_funcs} functions indexed from {len(scan_results)} files</span>',
            unsafe_allow_html=True, width="content",
            help="Each answer uses the four closest matches, so it can miss code elsewhere in the repo.",
        )
        st.space("stretch")
        new_scan_button("New scan", key="qa_new_scan_bottom", type="tertiary", icon=":material/refresh:")

    _render_history(history)

    # Pinned to the bottom of the page by Streamlit when called at the top level.
    prompt = st.chat_input("Ask about this repo, e.g. which function writes the output file?", key="qa_chat")

    chip_question = None
    chips_slot = st.empty()
    if not history:
        with chips_slot.container(horizontal=True, gap="small", key="qa_chips"):
            for i, question in enumerate(_starter_questions(scan_results), start=1):
                if st.button(question, key=f"qa_chip_{i}", type="secondary", icon=":material/arrow_outward:"):
                    chip_question = question

    question = (prompt or chip_question or "").strip()
    if not question:
        return

    chips_slot.empty()
    with st.chat_message("user", avatar=USER_AVATAR):
        st.text(question)
    with st.chat_message("assistant", avatar=ASSISTANT_AVATAR):
        with st.container(key="compact_qa_status"), \
                st.status(":shimmer[Finding the closest code]", type="compact", expanded=False) as status:
            st.caption("Searching this session's index for the four closest entries, then asking the model.")
            _audit_question(question)
            _process_and_append_qa(question)
            status.update(label="Searched the index", state="complete")
        answer = st.session_state["qa_chat_history"][-1]
        _render_answer(answer.get("content", ""), answer.get("citation"))
