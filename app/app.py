"""
CodeDocAI -- app.py
Configuration and routing hub. All CSS, fixtures, helpers, and screen
renderers live in separate modules; this file only wires them together.

Session history is preserved in the individual screen modules.
"""

import sys
from pathlib import Path
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

from dotenv import load_dotenv
load_dotenv()

# Ensure the app and project root directories are on sys.path so modules resolve in all execution contexts
_APP_DIR = Path(__file__).resolve().parent
_ROOT_DIR = _APP_DIR.parent
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))
if str(_ROOT_DIR) not in sys.path:
    sys.path.append(str(_ROOT_DIR))

import streamlit as st
import streamlit.components.v1 as components

# ---------------------------------------------------------------------------
# Page configuration -- MUST be the absolute first st.* call Streamlit allows.
# This is metadata only; it does not render any content.
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="CodeDocAI",
    page_icon="\U0001f7e1",
    layout="centered",
)

# ---------------------------------------------------------------------------
# CSS injection -- MUST be the first render call after set_page_config.
# The entire style block lives in styles.py; never add a second injection here.
# ---------------------------------------------------------------------------
try:
    from styles import inject_css
except ImportError:
    from app.styles import inject_css
inject_css()

# ---------------------------------------------------------------------------
# Session state & URL sync -- initialize keys and support browser back/next.
# ---------------------------------------------------------------------------
_VALID_SCREENS = {"landing", "scan", "generation", "docs", "qa", "foundation", "export", "architecture"}
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

# Keep browser URL query params synchronized with current_screen
if st.session_state["current_screen"] != _url_screen:
    if st.session_state["current_screen"] == "landing":
        if "screen" in st.query_params:
            del st.query_params["screen"]
    else:
        st.query_params["screen"] = st.session_state["current_screen"]

st.session_state["_prev_url_screen"] = st.query_params.get("screen")

# ---------------------------------------------------------------------------
# AI Engine Initialization (Cached to prevent RAM leaks during routing)
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def load_ai_engine():
    model_path = _ROOT_DIR / "my_docstring_project"
    try:
        try:
            tokenizer = AutoTokenizer.from_pretrained(str(model_path))
        except Exception:
            tokenizer = AutoTokenizer.from_pretrained(str(model_path), extra_special_tokens=[])
            
        model = AutoModelForSeq2SeqLM.from_pretrained(str(model_path))
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.to(device)
        model.eval()
        return tokenizer, model, device
    except Exception as e:
        print(f"[!] Warning: Local CodeT5 Engine failed to load: {e}. Falling back to Cloud Agent.")
        return None

# Mount the AI engine to session state so child screens can access it instantly
if "ai_engine" not in st.session_state:
    st.session_state["ai_engine"] = load_ai_engine()

# ---------------------------------------------------------------------------
# Screen imports (deferred so set_page_config + CSS fire first)
# ---------------------------------------------------------------------------
from screens.landing      import render_landing
from screens.scan         import render_scan
from screens.generation   import render_generation
from screens.docs         import render_documentation
from screens.qa           import render_qa
from screens.architecture import render_architecture
from screens.export       import render_export
from screens.foundation   import render_foundation

# ---------------------------------------------------------------------------
# Screen router
# ---------------------------------------------------------------------------
_screen = st.session_state.get("current_screen", "landing")
_last   = st.session_state.get("_last_screen", "landing")

# Inject scroll-to-top ONLY on a screen transition, never on same-screen reruns.
if _screen != _last:
    components.html(
        "<script>window.scrollTo(0, 0);</script>",
        height=0,
    )
    st.session_state["_last_screen"] = _screen

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
else:
    # Graceful fallback
    render_landing()