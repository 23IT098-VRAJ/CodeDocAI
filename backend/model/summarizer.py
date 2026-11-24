"""
backend/model/summarizer.py
Bridge between the pipeline and the cloud Docstring Writer agent, used only when
the local CodeT5 engine could not produce a docstring.
"""

from backend.agents.docwriter import generate_docstrings_batch


def summarize_batch(functions: list[dict]) -> dict[int, str]:
    """
    Drafts docstrings for up to one batch of functions with a single cloud request.

    Returns {index into `functions`: docstring} for every function that got one.
    Functions with no source are skipped. Raises if the cloud request fails, so the
    caller can stop instead of storing an error message as documentation.
    """
    indexed = [(i, fn) for i, fn in enumerate(functions) if (fn.get("source") or "").strip()]
    if not indexed:
        return {}

    docs = generate_docstrings_batch([fn for _, fn in indexed])
    return {indexed[pos][0]: doc for pos, doc in docs.items() if pos < len(indexed)}
