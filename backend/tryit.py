"""
The home page's "try it" box: drafts docstrings for a pasted snippet with the
same CodeT5 call and write-back the full pipeline uses, so what a visitor sees
there is what a scan would produce.
"""

import ast
import time
from typing import Any

from backend.parser.extractor import extract_definitions
from backend.pipeline import _local_docstrings
from backend.writer import insert_docstrings

MAX_SNIPPET_CHARS = 4000
MAX_SNIPPET_DRAFTS = 3


class SnippetError(ValueError):
    """A snippet the box can't draft for, with a message meant for the visitor."""


def draft_snippet(ai_engine: Any, code: str) -> dict:
    """
    Drafts a docstring for up to three undocumented functions in ``code``.

    Returns {"source": the code with the docstrings written in,
             "drafts": [(function name, docstring), ...], "seconds": model time}.
    Raises SnippetError with a visitor-facing message when it can't.
    """
    code = (code or "").replace("\r\n", "\n").strip("\n")
    if not code.strip():
        raise SnippetError("Paste a Python function to draft its docstring.")
    if len(code) > MAX_SNIPPET_CHARS:
        raise SnippetError(f"Keep the snippet under {MAX_SNIPPET_CHARS:,} characters; a scan handles whole files.")
    try:
        ast.parse(code)
    except SyntaxError as error:
        raise SnippetError(f"That isn't valid Python (line {error.lineno}). Check the indentation and brackets.") from None

    functions = [d for d in extract_definitions(code, "snippet.py") if d.get("kind") != "class"]
    if not functions:
        raise SnippetError("No function found. Paste code that contains a def.")
    missing = [d for d in functions if not d.get("has_docstring")][:MAX_SNIPPET_DRAFTS]
    if not missing:
        raise SnippetError("Every function here already has a docstring. Remove one to see a draft.")
    if not ai_engine:
        raise SnippetError("The docstring model isn't loaded on this server right now. Try again in a minute.")

    started = time.perf_counter()
    drafts = _local_docstrings(ai_engine, [d.get("code") or d.get("source") or "" for d in missing])
    seconds = time.perf_counter() - started

    for definition, draft in zip(missing, drafts, strict=True):
        definition["docstring"] = draft or ""
        definition["is_ai_draft"] = bool(draft)
    result = insert_docstrings(code, missing)
    if not result["inserted"]:
        raise SnippetError("The model couldn't draft this one. Try a function with a clearer body.")
    return {
        "source": result["source"],
        "drafts": [(d["name"], d["docstring"]) for d in missing if d["is_ai_draft"]],
        "seconds": seconds,
    }
