"""
CodeDocAI -- app.py
Configuration and routing hub. All CSS, helpers, and screen
renderers live in separate modules; this file only wires them together.

Session history is preserved in the individual screen modules.
"""

import logging
import os
import re
import sys
import time
import uuid
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# One import root for the app's own modules (helpers, styles, screens.*) and one for
# backend.*. Streamlit already adds this folder; the project root is added here.
_APP_DIR = Path(__file__).resolve().parent
_ROOT_DIR = _APP_DIR.parent
for _import_root in (_APP_DIR, _ROOT_DIR):
    if str(_import_root) not in sys.path:
        sys.path.append(str(_import_root))

import streamlit as st

# Libraries log warnings and worse; this project's own modules also log what they are doing.
logging.basicConfig(level=logging.WARNING, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
for _own_logger in ("codedocai", "backend", "helpers", "screens"):
    logging.getLogger(_own_logger).setLevel(logging.INFO)
logger = logging.getLogger("codedocai")

# torch and transformers are imported inside load_ai_engine, not here. At module
# level two visitors arriving on a cold server imported them at the same moment,
# and one of them crashed with "cannot import name 'AutoTokenizer'".

_VALID_SCREENS = {"landing", "scan", "generation", "docs", "qa", "foundation", "export", "architecture", "login", "manager_dashboard"}
_SCREEN_TITLES = {
    "scan": "Scan",
    "generation": "Generate",
    "docs": "Documentation",
    "qa": "Q&A",
    "export": "Export",
    "architecture": "How it works",
    "login": "Sign in",
    "manager_dashboard": "Audit log",
    "foundation": "Foundation",
}


def _resolve_screen() -> str:
    """The screen this run will show, from the URL and the session. Reads only; changes nothing."""
    url_screen = st.query_params.get("screen")
    current = st.session_state.get("current_screen")
    if url_screen in _VALID_SCREENS:
        if current is None or st.session_state.get("_prev_url_screen") != url_screen:
            return url_screen  # first visit, or the browser's back/forward button moved the URL
        return current
    return current or "landing"


def page_title(screen: str) -> str:
    """Each screen gets its own tab title, so tabs and history entries can be told apart."""
    name = _SCREEN_TITLES.get(screen)
    return f"{name} · CodeDocAI" if name else "CodeDocAI"


# ---------------------------------------------------------------------------
# Page configuration -- MUST be the absolute first st.* call Streamlit allows.
# This is metadata only; it does not render any content.
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title=page_title(_resolve_screen()),
    page_icon="\U0001f7e1",
    layout="centered",
)

# ---------------------------------------------------------------------------
# CSS injection -- MUST be the first render call after set_page_config.
# The entire style block lives in styles.py; never add a second injection here.
# ---------------------------------------------------------------------------
from styles import inject_css

inject_css()

# ---------------------------------------------------------------------------
# Session identity and refresh survival.
# A page refresh starts a new Streamlit session and would lose the scan. The
# session id therefore travels in the URL (?sid=...), and the work of each
# session is kept in server memory under that id. Nothing is written to disk,
# sign-in state is never restored, and old entries are dropped.
# ---------------------------------------------------------------------------
_PERSISTED_KEYS = [
    "scan_status", "scan_error_message", "scan_error_field", "scan_results", "scan_summary",
    "scan_github_url", "repo_source", "pipeline_results", "generation_attempt", "generation_complete",
    "qa_chat_history", "qa_answer_cache", "overview_context", "overview_error",
]
_MAX_STORED_SESSIONS = 25
_SESSION_TTL_SECONDS = 6 * 3600  # a session idle this long is dropped with its vector index


@st.cache_resource(show_spinner=False)
def _session_store() -> dict:
    return {}


def _save_session() -> None:
    store = _session_store()
    session_id = st.session_state.get("session_id")
    if not session_id:
        return
    now = time.time()
    store[session_id] = (now, {key: st.session_state.get(key) for key in _PERSISTED_KEYS})

    by_age = sorted(store.items(), key=lambda item: item[1][0])
    too_many = max(0, len(store) - _MAX_STORED_SESSIONS)
    stale = [sid for i, (sid, (saved_at, _)) in enumerate(by_age)
             if sid != session_id and (i < too_many or now - saved_at > _SESSION_TTL_SECONDS)]
    for stale_id in stale:
        _, state = store.pop(stale_id, (0, {}))
        _release_session(stale_id, state)


def _release_session(session_id: str, state: dict) -> None:
    """Frees what a dropped session still holds: its vector collection and any scan folder."""
    from backend.rag.vectorstore import reset_collection
    from backend.repo.loader import cleanup_repo
    from helpers import collection_name_for

    reset_collection(collection_name_for(session_id))
    cleanup_repo((state.get("repo_source") or {}).get("local_path"))


if "session_id" not in st.session_state:
    _url_sid = st.query_params.get("sid") or ""
    if re.fullmatch(r"[0-9a-f]{32}", _url_sid):
        st.session_state["session_id"] = _url_sid
        _saved = _session_store().get(_url_sid)
        if _saved:
            for _key, _value in _saved[1].items():
                st.session_state[_key] = _value
    else:
        # Identifies this browser session; also keeps its vector index separate from other users'.
        st.session_state["session_id"] = uuid.uuid4().hex

from backend.resilience.rate_limiter import offline_mode

_offline = offline_mode()

# ---------------------------------------------------------------------------
# Session state & URL sync -- initialize keys and support browser back/next.
# ---------------------------------------------------------------------------
_url_screen = st.query_params.get("screen")

if _url_screen in _VALID_SCREENS:
    st.session_state.setdefault("current_screen", _url_screen)
    if st.session_state.get("_prev_url_screen") != _url_screen:
        # Browser back / forward button changed the URL query param
        st.session_state["current_screen"] = _url_screen
else:
    st.session_state.setdefault("current_screen", "landing")

st.session_state.setdefault("scan_status", "idle")
st.session_state.setdefault("scan_error_message", None)
st.session_state.setdefault("scan_results", None)
st.session_state.setdefault("scan_summary", None)
st.session_state.setdefault("scan_github_url", "")
st.session_state.setdefault("repo_source", None)
st.session_state.setdefault("repo_overview", None)
st.session_state.setdefault("pipeline_results", None)
st.session_state.setdefault("generation_attempt", 0)
st.session_state.setdefault("generation_complete", False)
st.session_state.setdefault("_last_screen", "landing")
st.session_state.setdefault("qa_chat_history", [])
st.session_state.setdefault("qa_answer_cache", {})
st.session_state.setdefault("overview_context", None)
st.session_state.setdefault("overview_error", None)

# Keep browser URL query params synchronized with current_screen
if st.session_state["current_screen"] != _url_screen:
    if st.session_state["current_screen"] == "landing":
        if "screen" in st.query_params:
            del st.query_params["screen"]
    else:
        st.query_params["screen"] = st.session_state["current_screen"]
if st.query_params.get("sid") != st.session_state["session_id"]:
    st.query_params["sid"] = st.session_state["session_id"]

st.session_state["_prev_url_screen"] = st.query_params.get("screen")

# ---------------------------------------------------------------------------
# Housekeeping -- once per server start, remove scan folders that earlier
# sessions left behind (closed tab, crash). Recent folders are not touched.
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def _sweep_stale_scans_once() -> int:
    from backend.repo.loader import sweep_stale_scans
    removed = sweep_stale_scans()
    if removed:
        logger.info("Removed %d stale scan folder(s).", removed)
    return removed

_sweep_stale_scans_once()

# ---------------------------------------------------------------------------
# AI Engine Initialization (Cached to prevent RAM leaks during routing)
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def load_ai_engine() -> tuple | None:
    # Imported here so the heavy libraries load once, under the cache's lock.
    import torch
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
    from transformers.utils import logging as transformers_logging

    model_path = _ROOT_DIR / "my_docstring_project"
    # The checkpoint stores T5's shared and per-stack embeddings as separate tensors, and
    # transformers 5 prints three "tied weights" warnings about it on every load. They are
    # harmless (the separate tensors are used as trained, and the output is unchanged), and
    # the config can't switch them off because T5 ties those embeddings by design, so the
    # library's own warnings are muted for the duration of the load only.
    previous_verbosity = transformers_logging.get_verbosity()
    transformers_logging.set_verbosity_error()
    try:
        try:
            tokenizer = AutoTokenizer.from_pretrained(str(model_path))
        except Exception:  # noqa: BLE001 - older transformers reject this checkpoint's extra tokens
            tokenizer = AutoTokenizer.from_pretrained(str(model_path), extra_special_tokens=[])

        model = AutoModelForSeq2SeqLM.from_pretrained(str(model_path))
        transformers_logging.set_verbosity(previous_verbosity)
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.to(device)
        model.eval()
        return tokenizer, model, device
    except Exception as error:  # noqa: BLE001 - without the local model the cloud fallback drafts instead
        logger.warning("The local CodeT5 model failed to load (%s); the cloud fallback will draft instead.", error)
        return None
    finally:
        transformers_logging.set_verbosity(previous_verbosity)

# Mount the AI engine to session state so child screens can access it instantly
if "ai_engine" not in st.session_state:
    # Loading the weights takes a few seconds on a cold start; say so instead of showing a blank page.
    with st.spinner("Loading the CodeT5 model"):
        st.session_state["ai_engine"] = load_ai_engine()

# ---------------------------------------------------------------------------
# Screen imports (deferred so set_page_config + CSS fire first)
# ---------------------------------------------------------------------------
from screens.architecture import render_architecture
from screens.docs import render_documentation
from screens.export import render_export
from screens.foundation import render_foundation
from screens.generation import render_generation
from screens.landing import render_landing
from screens.login import render as render_login
from screens.manager_dashboard import render as render_manager
from screens.qa import render_qa
from screens.scan import render_scan


def _scroll_to_top() -> None:
    """A new screen starts at its top. Streamlit scrolls its main pane, not the window."""
    script = (
        "<script>(function () {"
        "var doc = (window.parent || window).document;"
        "var main = doc.querySelector('[data-testid=\"stMain\"]') || doc.querySelector('section.main');"
        "if (main) { main.scrollTo(0, 0); }"
        "(window.parent || window).scrollTo(0, 0);"
        "})();</script>"
    )
    # The keyed container is hidden by CSS. Rendered in the page flow, the script's element
    # added a gap above the screen on transitions only, so the header sat 16px lower then.
    with st.container(key="scroll_reset"):
        st.html(script, unsafe_allow_javascript=True)


# ---------------------------------------------------------------------------
# Screen router
# ---------------------------------------------------------------------------
_screen = st.session_state.get("current_screen", "landing")
_last   = st.session_state.get("_last_screen", "landing")

# Scroll to the top ONLY on a screen transition, never on same-screen reruns.
if _screen != _last:
    # A pending "are you sure?" belongs to the screen it was asked on.
    st.session_state["_confirm_new_scan"] = None
    st.session_state["_confirm_purge"] = None
    _scroll_to_top()
    st.session_state["_last_screen"] = _screen

# The design-token page is a development aid; outside test or dev mode it isn't reachable.
if _screen == "foundation" and not (_offline or os.environ.get("CODEDOCAI_DEV") == "1"):
    _screen = "landing"

from helpers import render_top_bar, show_queued_toasts

render_top_bar(_screen, offline=_offline)
show_queued_toasts()

try:
    if _screen == "foundation":
        render_foundation()
    elif _screen == "landing":
        render_landing()
    elif _screen == "scan":
        render_scan()
    elif _screen == "generation":
        render_generation()
    elif _screen == "docs":
        render_documentation()
    elif _screen == "qa":
        render_qa()
    elif _screen == "export":
        render_export()
    elif _screen == "architecture":
        render_architecture()
    elif _screen == "login":
        render_login()
    elif _screen == "manager_dashboard":
        render_manager()
    else:
        # Graceful fallback
        render_landing()
finally:
    # Runs on normal completion and when a screen ends the run with st.rerun() or st.stop().
    _save_session()
