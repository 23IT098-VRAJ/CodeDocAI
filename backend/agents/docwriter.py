"""
backend/agents/docwriter.py
Cloud fallback for docstring drafting. Several functions are sent in one request so a
failed local model cannot turn one scan into hundreds of API calls.
"""
import json

from backend.resilience.rate_limiter import execute_with_failover
from backend.security import redact

MAX_SOURCE_CHARS = 2000  # per function, keeps a batch well inside the context window


def _batch_prompt(items: list[dict]) -> str:
    blocks = []
    for i, item in enumerate(items):
        source = redact(item.get("source") or "")[:MAX_SOURCE_CHARS]
        blocks.append(
            f'ID: f{i}\nFunction `{item.get("name", "unknown")}` in `{item.get("file", "")}`:\n'
            f"```python\n{source}\n```"
        )
    return (
        "Write a one-line docstring for each Python function below: one sentence in the imperative "
        "mood saying what the function does, ending with a period, at most 15 words "
        '(for example "Convert a file to a set."). No Args or Returns sections, so these match the '
        "summaries the local model writes for the rest of the project.\n\n"
        + "\n\n".join(blocks)
        + "\n\nYou MUST output exactly one valid JSON object that maps every ID to its docstring text, "
        'for example {"f0": "Return the domain name of a URL.", "f1": "..."}.\n'
        "Do NOT include the triple quotes. Output ONLY the raw JSON. "
        "Do NOT wrap it in ```json blocks. Do NOT include any conversational text."
    )


def _clean_docstring(text: str) -> str:
    text = text.strip()
    for quote in ('"""', "'''"):
        if text.startswith(quote) and text.endswith(quote) and len(text) >= 6:
            text = text[3:-3].strip()
    return text


def parse_batch_response(raw: str, count: int) -> dict[int, str]:
    """
    Turns the model's JSON reply into {item index: docstring}.
    Unparseable replies and missing or empty entries are simply left out.
    """
    cleaned = raw.replace("```json", "").replace("```", "").strip()
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start == -1 or end <= start:
        return {}
    try:
        data = json.loads(cleaned[start:end + 1])
    except json.JSONDecodeError:
        return {}
    if not isinstance(data, dict):
        return {}

    docs = {}
    for i in range(count):
        value = data.get(f"f{i}")
        if isinstance(value, str) and _clean_docstring(value):
            docs[i] = _clean_docstring(value)
    return docs


def _batch_logic(llm, items: list[dict]) -> dict[int, str]:
    from crewai import Agent, Crew, Process, Task

    writer_agent = Agent(
        role="Senior Python Documentation Engineer",
        goal="Write one-line summary docstrings for undocumented Python functions.",
        backstory=(
            "You are a PEP 257 standards specialist. You read function signatures, "
            "arguments, and execution bodies to extract intent, parameters, and return types. "
            "You write short, plain one-line summaries without preamble."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )
    doc_task = Task(
        description=_batch_prompt(items),
        expected_output="A raw JSON object mapping each function ID to its docstring text.",
        agent=writer_agent,
    )
    crew = Crew(agents=[writer_agent], tasks=[doc_task], process=Process.sequential)
    result = crew.kickoff()
    return parse_batch_response(str(result), len(items))


def _offline_batch(items: list[dict]) -> dict[int, str]:
    return {
        i: f"[OFFLINE TEST] Placeholder docstring for {item.get('name', 'unknown')}."
        for i, item in enumerate(items)
    }


def generate_docstrings_batch(items: list[dict]) -> dict[int, str]:
    """
    Drafts docstrings for a batch of functions in a single cloud request.
    Each item needs "name", "source" and "file". Returns {item index: docstring}
    for the functions the model answered; raises if the request itself fails.
    """
    if not items:
        return {}
    return execute_with_failover(
        lambda llm: _batch_logic(llm, items),
        offline_result=lambda: _offline_batch(items),
    )
