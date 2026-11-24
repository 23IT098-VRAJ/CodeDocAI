"""
backend/coverage.py
Documentation coverage of a scan: how many functions and classes had a docstring
before the pipeline ran, and how many have one after it.

Functions and methods are counted together. Classes are reported separately because
their docstrings are not drafted: the local model is trained on functions only.
Module docstrings are reported as present or absent per file.
"""


def _percent(part: int, total: int) -> int | None:
    return round(100 * part / total) if total else None


def build_coverage(files: list[dict]) -> dict:
    """
    files are the pipeline’s per-file records: {"path", "module_doc", "functions": [definitions]}.
    """
    rows = []
    for file_info in files:
        definitions = file_info.get("functions") or []
        functions = [d for d in definitions if d.get("kind", "function") != "class"]
        classes = [d for d in definitions if d.get("kind") == "class"]
        rows.append({
            "path": file_info.get("path", "unknown"),
            "functions": len(functions),
            "functions_before": sum(1 for d in functions if d.get("has_docstring")),
            "functions_after": sum(1 for d in functions if (d.get("docstring") or "").strip()),
            "classes": len(classes),
            "classes_documented": sum(1 for d in classes if (d.get("docstring") or "").strip()),
            "module_docstring": bool((file_info.get("module_doc") or "").strip()),
        })

    def total(key: str) -> int:
        return sum(row[key] for row in rows)

    functions = total("functions")
    before = total("functions_before")
    after = total("functions_after")
    return {
        "files": rows,
        "file_count": len(rows),
        "functions": functions,
        "functions_before": before,
        "functions_after": after,
        "functions_before_pct": _percent(before, functions),
        "functions_after_pct": _percent(after, functions),
        "docstrings_drafted": after - before,
        "classes": total("classes"),
        "classes_documented": total("classes_documented"),
        "files_with_module_docstring": sum(1 for row in rows if row["module_docstring"]),
    }


def coverage_table(coverage: dict) -> str:
    """Per-file coverage as a Markdown table."""
    lines = [
        "| File | Functions | Documented before | Documented after | Classes documented | Module docstring |",
        "|---|---:|---:|---:|---:|:---:|",
    ]
    for row in coverage.get("files", []):
        classes = f"{row['classes_documented']} / {row['classes']}" if row["classes"] else "-"
        lines.append(
            f"| `{row['path']}` | {row['functions']} | {row['functions_before']} | {row['functions_after']} "
            f"| {classes} | {'yes' if row['module_docstring'] else 'no'} |"
        )
    return "\n".join(lines)


def coverage_markdown(coverage: dict) -> str:
    """The whole coverage report as a Markdown document."""
    def pct(value) -> str:
        return "n/a" if value is None else f"{value}%"

    lines = [
        "# CodeDocAI Documentation Coverage",
        "",
        f"- Files scanned: {coverage.get('file_count', 0)}",
        f"- Functions and methods: {coverage.get('functions', 0)}",
        f"- Documented before the scan: {coverage.get('functions_before', 0)} ({pct(coverage.get('functions_before_pct'))})",
        f"- Documented after the scan: {coverage.get('functions_after', 0)} ({pct(coverage.get('functions_after_pct'))})",
        f"- Docstrings drafted: {coverage.get('docstrings_drafted', 0)}",
        f"- Classes with a docstring: {coverage.get('classes_documented', 0)} of {coverage.get('classes', 0)} "
        "(CodeDocAI doesn’t draft class docstrings)",
        f"- Files with a module docstring: {coverage.get('files_with_module_docstring', 0)} of {coverage.get('file_count', 0)}",
        "",
        "## By file",
        "",
        coverage_table(coverage),
        "",
    ]
    return "\n".join(lines)
