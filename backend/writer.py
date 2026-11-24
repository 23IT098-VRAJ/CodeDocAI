"""
backend/writer.py
Writes the drafted docstrings back into the source files, so the result of a scan
is documented code and not only a report about it.

Only AI-drafted docstrings are inserted; code that already had a docstring is never
touched. Every rewritten file is re-parsed before it is accepted, so the documented
copy is always valid Python.
"""
import ast
import difflib


def format_docstring(text: str, indent: str) -> list[str]:
    """The docstring as source lines, indented to sit as the first statement of a body."""
    text = text.strip().replace("\\", "\\\\").replace('"""', "'''")
    lines = [line.rstrip() for line in text.splitlines()]

    if len(lines) == 1:
        body = lines[0]
        if body.endswith('"'):
            body = body[:-1] + '\\"'  # a quote right before the closing quotes would end the string early
        return [f'{indent}"""{body}"""']

    formatted = [f'{indent}"""{lines[0]}']
    formatted.extend(f"{indent}{line}" if line else "" for line in lines[1:])
    formatted.append(f'{indent}"""')
    return formatted


def _documented_count(source: str) -> int | None:
    """Number of functions and classes with a docstring, or None if the source does not parse."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    nodes = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
    return sum(1 for node in ast.walk(tree) if isinstance(node, nodes) and ast.get_docstring(node))


def insert_docstrings(source: str, definitions: list[dict]) -> dict:
    """
    Inserts each AI-drafted docstring as the first statement of its function.

    definitions are the entries produced by extract_definitions for this source,
    after the pipeline filled in "docstring" and "is_ai_draft".

    Returns {"source": new source, "inserted": count, "skipped": [names]}.
    A definition is skipped when its body shares a line with the header
    (`def f(): return 1`). If the rewritten file would not parse, nothing is
    inserted and the original source is returned.
    """
    targets = [
        d for d in definitions
        if d.get("is_ai_draft") and (d.get("docstring") or "").strip() and d.get("body_lineno")
    ]
    if not targets:
        return {"source": source, "inserted": 0, "skipped": []}

    # Files saved with Windows line endings keep them; inserted lines get the same ending.
    crlf = "\r\n" in source and source.count("\n") == source.count("\r\n")
    original = source
    if crlf:
        source = source.replace("\r\n", "\n")

    lines = source.split("\n")
    inserted = 0
    skipped = []

    # Bottom-up, so earlier line numbers stay valid while lines are added below them.
    for definition in sorted(targets, key=lambda d: d["body_lineno"], reverse=True):
        index = definition["body_lineno"] - 1
        if index >= len(lines):
            skipped.append(definition["name"])
            continue
        line = lines[index]
        if line[:definition.get("body_col", 0)].strip():
            skipped.append(definition["name"])  # body is on the header line
            continue
        indent = line[:len(line) - len(line.lstrip())]
        lines[index:index] = format_docstring(definition["docstring"], indent)
        inserted += 1

    new_source = "\n".join(lines)
    before = _documented_count(source)
    after = _documented_count(new_source)
    if before is None or after is None or after != before + inserted:
        return {"source": original, "inserted": 0, "skipped": [d["name"] for d in targets]}

    if crlf:
        new_source = new_source.replace("\n", "\r\n")
    return {"source": new_source, "inserted": inserted, "skipped": skipped}


def make_patch(path: str, old_source: str, new_source: str) -> str:
    """Unified diff of one file, in the a/ b/ form that `git apply` and `patch -p1` accept."""
    def split(text: str) -> list[str]:
        return (text[:-1] if text.endswith("\n") else text).split("\n")

    diff = difflib.unified_diff(
        split(old_source), split(new_source),
        fromfile=f"a/{path}", tofile=f"b/{path}", lineterm="",
    )
    body = "\n".join(diff)
    return body + "\n" if body else ""
