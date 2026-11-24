"""
screens/docs.py -- CodeDocAI
Renders the dynamically generated AI documentation and module overviews.
"""

import html as _html
import re

import streamlit as st

from backend.coverage import coverage_table
from backend.pipeline import load_results_cache
from components import copy_text
from components.diff_view import function_diff, render_diff
from helpers import page_heading, render_stats


def definition_title(fn: dict) -> str:
    """
    Expander title for a function or class: the name in code style plus a badge for
    its docstring state. Inline code keeps underscores literal, so `__init__` stays
    `__init__` instead of turning into a bold "init".
    """
    name = fn.get("name", "unknown").replace("`", "")
    docstring = fn.get("docstring") or ""
    is_class = fn.get("kind") == "class"
    if fn.get("is_ai_draft"):
        badge = " :orange-badge[Draft]"
    elif not docstring and is_class:
        badge = " :gray-badge[No docstring]"
    elif not docstring:
        badge = " :red-badge[Not generated]"
    else:
        badge = ""
    return (f"`class {name}`" if is_class else f"`{name}()`") + badge


FILTER_OPTIONS = ["Everything", "AI drafts", "No docstring", "Already documented"]


def filter_definitions(definitions: list, query: str = "", show: str = "Everything") -> list:
    """
    The functions and classes that match the docs-screen filter.
    query matches the name or the file path, ignoring case; show narrows by docstring state.
    """
    needle = (query or "").strip().lower()
    kept = []
    for fn in definitions:
        has_docstring = bool((fn.get("docstring") or "").strip())
        if show == "AI drafts" and not fn.get("is_ai_draft"):
            continue
        if show == "No docstring" and has_docstring:
            continue
        if show == "Already documented" and (fn.get("is_ai_draft") or not has_docstring):
            continue
        if needle and needle not in fn.get("name", "").lower() and needle not in fn.get("file", "").lower():
            continue
        kept.append(fn)
    return kept


# The segmented control's labels and the filter states they stand for.
SHOW_CHOICES = {"All": "Everything", "Drafted": "AI drafts", "Missing": "No docstring"}


def signature(fn: dict) -> str:
    """The definition's header line without `def`/`async def` and the trailing colon, e.g. `crawl(url)`."""
    is_class = fn.get("kind") == "class"
    name = fn.get("name", "unknown")
    for line in (fn.get("source") or "").splitlines():
        stripped = line.strip()
        if stripped.startswith(("def ", "async def ", "class ")):
            header = stripped.split(" ", 2)[-1] if stripped.startswith("async def ") else stripped.split(" ", 1)[1]
            header = header.rstrip(":").strip()
            if header.count("(") > header.count(")"):  # parameters continue on the next lines
                header = header.split("(", 1)[0] + "(…)"
            # Methods are named Class.method; the header only knows the method's own name.
            if "." in name and not is_class:
                header = name.rsplit(".", 1)[0] + "." + header
            return ("class " if is_class else "") + header
    return f"class {name}" if is_class else f"{name}()"


def status_badge(fn: dict) -> tuple[str, str] | None:
    """(label, colour) for the definition's docstring state; None when it was already documented."""
    if fn.get("is_ai_draft"):
        return "Draft", "orange"
    if not (fn.get("docstring") or "").strip():
        return ("No docstring", "gray") if fn.get("kind") == "class" else ("Not generated", "red")
    return None


def _literal(text: str) -> str:
    """HTML-escaped text whose underscores and asterisks markdown can't turn into bold or italics."""
    return _html.escape(text).replace("_", "&#95;").replace("*", "&#42;")


def file_coverage(definitions: list) -> tuple[int, int]:
    """(documented, total) over one file's definitions."""
    return sum(1 for fn in definitions if (fn.get("docstring") or "").strip()), len(definitions)


def _render_coverage(coverage: dict) -> None:
    """Before/after documentation coverage of this scan."""
    if not coverage or not coverage.get("file_count"):
        return  # results saved by an older version carry no coverage data

    def pct(value) -> str:
        return "n/a" if value is None else f"{value}%"

    render_stats([
        ("Before", pct(coverage.get("functions_before_pct"))),
        ("After", pct(coverage.get("functions_after_pct"))),
        ("Drafted", coverage.get("docstrings_drafted", 0)),
        ("Functions documented", f"{coverage.get('functions_after', 0)}/{coverage.get('functions', 0)}"),
    ], key="docs_stats")
    with st.expander("Coverage table", type="compact", key="compact_coverage"):
        st.caption(
            "Classes and modules aren’t drafted: "
            f"{coverage.get('classes_documented', 0)} of {coverage.get('classes', 0)} classes and "
            f"{coverage.get('files_with_module_docstring', 0)} of {coverage.get('file_count', 0)} files have one."
        )
        st.markdown(coverage_table(coverage))


def _render_definition(fn: dict, diff_mode: bool = False) -> None:
    docstring = (fn.get("docstring") or "").strip()
    # Component keys may not contain "__" (Spider.__init__ would), so runs of non-word characters
    # and underscores collapse to one underscore.
    row_key = re.sub(r"[\W_]+", "_", f"{fn.get('file', '')}_{fn.get('name', '')}").strip("_")
    with st.container(key=f"docs_fn_{row_key}", gap="xxsmall"):
        with st.container(horizontal=True, vertical_alignment="center", gap="small"):
            st.markdown(f'<code class="docs-sig">{_literal(signature(fn))}</code>',
                        unsafe_allow_html=True, width="content")
            badge = status_badge(fn)
            if badge:
                st.badge(badge[0], color=badge[1])
        change = function_diff(fn)
        if diff_mode and change:
            render_diff(*change, title=signature(fn), key=f"diff_inline_{row_key}")
            return
        if docstring:
            copy_text.docstring(docstring, key=f"doc_copy_{row_key}")
        elif fn.get("kind") == "class":
            st.caption("Class docstrings aren’t drafted: the local model learned from functions only.")
        else:
            st.caption("Neither the local model nor the cloud fallback drafted this one.")
        with st.expander("Source", type="compact", key=f"compact_src_{row_key}"):
            if change:
                render_diff(*change, title=signature(fn), key=f"diff_src_{row_key}", context=1000)
            else:
                st.code(fn.get("source", ""), language="python")


@st.fragment
def _render_function_list(everything: list) -> None:
    """Search and the state filter rerun only this list, not the page."""
    with st.container(horizontal=True, vertical_alignment="bottom", gap="small", key="docs_filters"):
        query = st.text_input("Search", key="docs_filter", placeholder="Name or file, e.g. spider.py")
        show_label = st.segmented_control("Show", list(SHOW_CHOICES), default="All", required=True,
                                          key="docs_filter_show")
        diff_mode = st.toggle("Diff view", key="docs_diff_mode",
                              help="Show each drafted docstring as the change it makes to the code.")
    functions = filter_definitions(everything, query, SHOW_CHOICES.get(show_label or "All", "Everything"))
    if len(functions) != len(everything):
        st.caption(f"Showing {len(functions)} of {len(everything)}")
    if everything and not functions:
        st.info("Nothing matches this filter. Clear the search or choose All.")

    by_file: dict[str, list] = {}
    for fn in functions:
        by_file.setdefault(fn.get("file", "unknown"), []).append(fn)
    all_by_file: dict[str, list] = {}
    for fn in everything:
        all_by_file.setdefault(fn.get("file", "unknown"), []).append(fn)

    for file_path, funcs in by_file.items():
        documented, total = file_coverage(all_by_file.get(file_path, funcs))
        percent = round(100 * documented / total) if total else 0
        with st.container(border=True, key=f"docs_file_{file_path}".replace("/", "_").replace(".", "_")):
            st.markdown(
                '<div class="docs-file-head">'
                f'<h2 class="docs-file-name">{_literal(file_path)}</h2>'
                f'<span class="docs-file-count">{documented}/{total} documented</span>'
                f'<span class="docs-file-bar" role="img" aria-label="{percent}% documented">'
                f'<span style="width:{percent}%"></span></span>'
                '</div>',
                unsafe_allow_html=True,
            )
            for fn in funcs:
                _render_definition(fn, diff_mode)


def render_documentation() -> None:
    if st.session_state.get("current_screen") != "docs":
        return

    page_heading("Documentation")

    pipeline_data = st.session_state.get("pipeline_results")

    # Optional disk cache (CODEDOCAI_DISK_CACHE=1): re-hydrate session state after a page refresh
    if not pipeline_data:
        pipeline_data = load_results_cache()
        if pipeline_data:
            st.session_state["pipeline_results"] = pipeline_data

    if not pipeline_data:
        st.markdown('<p class="docs-empty-sub">Run a scan and generate documentation first.</p>',
                    unsafe_allow_html=True)
        if st.button("Start a scan", key="docs_empty_scan", type="primary"):
            st.session_state["current_screen"] = "scan"
            st.rerun()
        return

    _render_coverage(pipeline_data.get("coverage"))

    with st.container(border=True, key="docs_overview"):
        st.markdown(pipeline_data.get("overview", "No architecture overview generated."))

    _render_function_list(pipeline_data.get("functions", []))

    with st.container(horizontal=True, gap="small", key="docs_actions"):
        if st.button("Ask a question", key="docs_ask", type="primary"):
            st.session_state["current_screen"] = "qa"
            st.rerun()
        if st.button("Back to scan", key="docs_back", type="tertiary", icon=":material/arrow_back:"):
            st.session_state["current_screen"] = "scan"
            st.rerun()
