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
from components import copy_text
from helpers import (
    audit_event,
    new_scan_button,
    page_heading,
    session_collection_name,
    skeleton,
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


def without_markers(text: str) -> str:
    """The answer without the [S1]-style block numbers the model cites; the source pills show them."""
    text = _re.sub(r"\s*\((?:\s*\[S\d+\]\s*,?)+\)", "", text)
    return _re.sub(r"\s*\[S\d+\]", "", text)


def _render_answer(content: str, citation: str | None, key: str) -> None:
    st.markdown(without_markers(content))
    if citation:
        copy_text.pills([part.strip() for part in citation.split("|") if part.strip()], key=key)


def _stream_words(text: str):
    """Yields the answer a few words at a time; the whole stream takes at most about a second."""
    import time

    words = text.split(" ")
    delay = min(0.03, 1.0 / max(len(words), 1))
    for i, word in enumerate(words):
        yield word + (" " if i < len(words) - 1 else "")
        time.sleep(delay)


def _render_history(history: list) -> None:
    for index, message in enumerate(history):
        if message.get("role") == "user":
            with st.chat_message("user", avatar=USER_AVATAR):
                st.text(message.get("content", ""))
        else:
            with st.chat_message("assistant", avatar=ASSISTANT_AVATAR):
                _render_answer(message.get("content", ""), message.get("citation"), key=f"qa_cite_{index}")


# The same four for every repository: each works on any codebase and covers what newcomers ask first.
STARTER_QUESTIONS = [
    "What is this project about?",
    "How do the main modules fit together?",
    "Where does the program start running?",
    "How are errors handled?",
]


def _how_strip(results: dict, file_count: int) -> str:
    """How an answer is put together, as three steps across the page."""
    functions = results.get("functions") or []
    defs = sum(1 for fn in functions if fn.get("kind") != "class")
    overview = " and the overview" if results.get("overview_status") == "ok" else ""
    steps = (
        ("Match", f"Your question is compared with {defs} functions, {file_count} file "
                  f"summar{'ies' if file_count != 1 else 'y'}{overview}."),
        ("Answer", "The four closest go to Gemini, with Groq as backup, and it answers from those only."),
        ("Cite", "Each answer names the functions it used, so you can open and check them."),
    )
    items = "".join(
        f'<li class="how-step"><span class="how-num">{i}</span><span class="how-name">{name}</span>'
        f'<span class="how-text">{_html.escape(text)}</span></li>'
        for i, (name, text) in enumerate(steps, start=1)
    )
    return f'<h2 class="qa-side-h">How an answer is built</h2><ol class="how-strip">{items}</ol>'


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
            f'{total_funcs} functions indexed from {len(scan_results)} files</span>'
            '<span class="qa-meta-note">Each answer reads the four closest matches</span>',
            unsafe_allow_html=True, width="content",
        )
        new_scan_button("New scan", key="qa_new_scan_bottom", type="secondary", icon=":material/refresh:")

    _render_history(history)

    # Pinned to the bottom of the page by Streamlit when called at the top level.
    prompt = st.chat_input("Ask about this repo, e.g. which function writes the output file?", key="qa_chat")

    chip_question = None
    chips_slot = st.empty()
    if not history:
        results = st.session_state.get("pipeline_results") or {}
        with chips_slot.container(key="qa_empty"):
            st.html('<h2 class="qa-side-h">Start with a question</h2>')
            with st.container(key="qa_chips"):
                columns = st.columns(len(STARTER_QUESTIONS), gap="small")
                for column, (i, starter) in zip(columns, enumerate(STARTER_QUESTIONS, start=1), strict=True):
                    with column:
                        if st.button(starter, key=f"qa_chip_{i}", type="secondary", width="stretch",
                                     icon=":material/arrow_outward:"):
                            chip_question = starter
            st.html('<p class="qa-hint">Or type your own below. A short follow-up such as “and where is it '
                    'called?” is read together with your previous question.</p>')
            st.html(_how_strip(results, len(scan_results)))

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
        loading = skeleton(3)
        _audit_question(question)
        _process_and_append_qa(question)
        # A blocked question never reaches the index or the model, so the label must not say it searched.
        blocked = classify_question(question) == "CRITICAL"
        status.update(label="Blocked on this machine, nothing searched" if blocked else "Searched the index",
                      state="complete")
        loading.empty()
        answer = st.session_state["qa_chat_history"][-1]
        st.write_stream(_stream_words(without_markers(answer.get("content", ""))))
        citation = answer.get("citation")
        if citation:
            copy_text.pills([part.strip() for part in citation.split("|") if part.strip()], key="qa_cite_live")
