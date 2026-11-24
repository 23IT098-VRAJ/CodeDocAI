"""
backend/resilience/rate_limiter.py
Load balancer and failover router for the cloud LLM calls made by the CrewAI agents.

Offline test mode
-----------------
Set CODEDOCAI_OFFLINE in the environment (or .env) to exercise the app without
spending API quota:

    CODEDOCAI_OFFLINE=1      every cloud call returns a canned response
    CODEDOCAI_OFFLINE=fail   every cloud call fails like an exhausted quota

In both modes no API key is read and no request leaves the machine.
"""
import contextlib
import logging
import os
import re
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

from backend.storage import read_json, update_json

logger = logging.getLogger(__name__)

_ROOT_DIR = Path(__file__).resolve().parents[2]
_COOLDOWN_FILE = _ROOT_DIR / "api_cooldowns.json"
_COOLDOWN_SECONDS = 120  # 2-minute cooling period
_MAX_ATTEMPTS = 4
_REQUEST_TIMEOUT_SECONDS = 90  # one cloud request; a hung call must not freeze the screen
_OFFLINE_ENV = "CODEDOCAI_OFFLINE"

# Priority hierarchy: Gemini first, Groq as fallback.
_HIERARCHY = [
    ("GEMINI_1", "gemini/gemini-3.6-flash"),
    ("GEMINI_2", "gemini/gemini-3.6-flash"),
    ("GROQ_1", "groq/openai/gpt-oss-120b"),
    ("GROQ_2", "groq/openai/gpt-oss-120b"),
]

# Errors worth retrying on another key. Matched as whole phrases: a bare
# "rate" would also match "generate" and cool down a healthy key.
_TRANSIENT_PATTERNS = [
    r"\b429\b",
    r"\b503\b",
    r"\b404\b",
    r"quota",
    r"rate[\s_-]?limit",
    r"too many requests",
    r"resource[\s_]exhausted",
    r"unavailable",
    r"overloaded",
    r"model[\s_]?not[\s_]?found",
    r"\bNotFoundError",      # litellm's exception for a model the provider dropped
    r"timed?[\s_-]?out",
    r"Timeout",
]
_TRANSIENT_RE = re.compile("|".join(_TRANSIENT_PATTERNS), re.IGNORECASE)


class AllKeysCoolingError(Exception):
    """Every configured API key is inside its cooldown window."""


class NoApiKeysError(Exception):
    """No API key is configured at all."""


def _load_dotenv() -> None:
    with contextlib.suppress(ImportError):
        from dotenv import load_dotenv

        load_dotenv()


def offline_mode() -> str:
    """Returns "" for live calls, "canned" for canned responses, "fail" for simulated outage."""
    _load_dotenv()
    value = os.environ.get(_OFFLINE_ENV, "").strip().lower()
    if value in ("", "0", "false", "no", "off"):
        return ""
    if value == "fail":
        return "fail"
    return "canned"


def get_keys() -> dict[str, str | None]:
    _load_dotenv()

    gemini_1 = os.environ.get("GEMINI_API_KEY_1")
    gemini_2 = os.environ.get("GEMINI_API_KEY_2")
    groq_1 = os.environ.get("GROQ_API_KEY_1")
    groq_2 = os.environ.get("GROQ_API_KEY_2")

    # Outside a Streamlit run, or without a secrets file, st.secrets raises; the .env values stand.
    with contextlib.suppress(Exception):
        import streamlit as st

        gemini_1 = st.secrets.get("GEMINI_API_KEY_1", gemini_1)
        gemini_2 = st.secrets.get("GEMINI_API_KEY_2", gemini_2)
        groq_1 = st.secrets.get("GROQ_API_KEY_1", groq_1)
        groq_2 = st.secrets.get("GROQ_API_KEY_2", groq_2)

    return {
        "GEMINI_1": gemini_1,
        "GEMINI_2": gemini_2,
        "GROQ_1": groq_1,
        "GROQ_2": groq_2,
    }


def _load_state() -> dict[str, float]:
    return read_json(_COOLDOWN_FILE, {})


def _mark_cooling(provider_id: str) -> None:
    until = time.time() + _COOLDOWN_SECONDS
    update_json(_COOLDOWN_FILE, lambda state: {**state, provider_id: until}, {})


def _is_transient(error: Exception) -> bool:
    """True when the error means 'this key/provider is busy or gone', so another key may work."""
    return bool(_TRANSIENT_RE.search(str(error)))


def _build_llm(model_str: str, api_key: str) -> Any:
    from crewai import LLM

    return LLM(model=model_str, api_key=api_key, timeout=_REQUEST_TIMEOUT_SECONDS)


def _get_active_llm() -> tuple[Any, str]:
    state = _load_state()
    now = time.time()
    keys = get_keys()
    any_key = False

    for pid, model_str in _HIERARCHY:
        key_val = keys.get(pid)
        if not key_val or not key_val.strip():
            continue
        any_key = True

        if now > state.get(pid, 0):
            # The key goes to this LLM object only. Writing it into os.environ would
            # let two sessions running at once overwrite each other's choice.
            return _build_llm(model_str, key_val), pid

    if not any_key:
        raise NoApiKeysError("No API key found. Add at least one to the .env file.")
    raise AllKeysCoolingError("Every API key hit a rate limit and is cooling down for 2 minutes.")


def execute_with_failover(
    agent_builder_func: Callable[[Any], Any],
    offline_result: Callable[[], Any] | None = None,
) -> Any:
    """
    Runs one cloud task. On a transient error (rate limit, outage, dropped model) the key
    is put into a 2-minute cooldown and the task is retried on the next available key.
    Any other error is raised immediately without touching the cooldown state.

    offline_result supplies the canned response used when CODEDOCAI_OFFLINE is set.
    """
    mode = offline_mode()
    if mode == "fail":
        raise AllKeysCoolingError(
            "Simulated cloud outage (CODEDOCAI_OFFLINE=fail); nothing called an API."
        )
    if mode == "canned":
        if offline_result is None:
            raise RuntimeError("Offline mode is on but this call has no canned response.")
        return offline_result()

    last_error: Exception | None = None
    for _ in range(_MAX_ATTEMPTS):
        try:
            active_llm, active_pid = _get_active_llm()
        except AllKeysCoolingError as cooling:
            if last_error is None:
                raise
            # Say what actually went wrong, not only that every key is now benched.
            raise AllKeysCoolingError(f"{cooling} Last error: {last_error}") from last_error
        logger.info("[failover] Sending the request to %s", active_pid)
        try:
            return agent_builder_func(active_llm)
        except Exception as error:
            logger.warning("[failover] %s returned an error: %s", active_pid, error)
            if not _is_transient(error):
                raise
            logger.warning("[failover] %s is rate-limited or down; cooling it for %ss.", active_pid, _COOLDOWN_SECONDS)
            _mark_cooling(active_pid)
            last_error = error

    raise RuntimeError("All failover attempts exhausted.") from last_error
