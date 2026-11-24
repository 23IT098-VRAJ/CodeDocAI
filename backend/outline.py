"""
backend/outline.py
Compact text outlines of the scanned code, built locally from the AST results and
the drafted docstrings. They feed the repository overview prompt and the per-file
entries of the vector index, so the cloud model sees what every file does instead
of the first few hundred characters of a handful of files.
"""

MAX_LINE_CHARS = 160
MAX_FUNCTIONS_PER_FILE = 30
MAX_OUTLINE_CHARS = 12000


def first_line(text: str | None, limit: int = MAX_LINE_CHARS) -> str:
    """First non-empty line of a docstring, without surrounding quotes."""
    for line in (text or "").splitlines():
        line = line.strip().strip('"\'').strip()
        if line:
            return line[:limit]
    return ""


def function_line(fn: dict) -> str:
    label = fn.get("signature") or f"{fn.get('name', 'unknown')}()"
    summary = first_line(fn.get("docstring"))
    return f"- {label}: {summary}" if summary else f"- {label}"


def file_outline(file_info: dict, max_functions: int = MAX_FUNCTIONS_PER_FILE) -> str:
    """
    One file as text. file_info needs "path", "module_doc" and "functions"
    (the class and function entries produced by the pipeline).
    """
    lines = [f"FILE: {file_info.get('path', 'unknown')}"]
    purpose = first_line(file_info.get("module_doc"))
    if purpose:
        lines.append(f"Purpose: {purpose}")

    functions = file_info.get("functions") or []
    if not functions:
        lines.append("Contents: no classes or functions")
        return "\n".join(lines)

    lines.append("Contents:")
    lines.extend(function_line(fn) for fn in functions[:max_functions])
    if len(functions) > max_functions:
        lines.append(f"... and {len(functions) - max_functions} more")
    return "\n".join(lines)


def repository_outline(files: list[dict], max_chars: int = MAX_OUTLINE_CHARS) -> str:
    """
    Every file's outline joined into one prompt-sized text. Files that do not fit
    in the budget are listed by name so the model still knows they exist.
    """
    blocks = []
    omitted = []
    used = 0
    for file_info in files:
        block = file_outline(file_info)
        if used + len(block) > max_chars:
            omitted.append(file_info.get("path", "unknown"))
            continue
        blocks.append(block)
        used += len(block) + 2

    text = "\n\n".join(blocks)
    if omitted:
        shown = ", ".join(omitted[:40])
        more = f" and {len(omitted) - 40} others" if len(omitted) > 40 else ""
        text += f"\n\n{len(omitted)} more files not shown in detail: {shown}{more}"
    return text
