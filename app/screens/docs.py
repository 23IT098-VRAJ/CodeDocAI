"""
screens/docs.py -- CodeDocAI
Renders the dynamically generated AI documentation and module overviews.
"""

import html as _html
import re

import streamlit as st

from backend.coverage import coverage_table
from backend.pipeline import MAX_LOCAL_DRAFTS, load_results_cache
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

    total = coverage.get("functions", 0)
    after = coverage.get("functions_after", 0)
    drafted = coverage.get("docstrings_drafted", 0)
    render_stats([
        ("Coverage before", pct(coverage.get("functions_before_pct"))),
        ("Coverage after", pct(coverage.get("functions_after_pct"))),
        ("Drafted this run", drafted),
        ("Functions with a docstring", f"{after}/{total}"),
    ], key="docs_stats", count_up=True)
    if drafted >= MAX_LOCAL_DRAFTS and after < total:
        st.caption(
            f"Drafting stops at {MAX_LOCAL_DRAFTS:,} functions per scan, so {total - after:,} still have no "
            "docstring. Scan a subfolder of the repository to draft the rest."
        )
    with st.expander("Coverage table", type="compact", key="compact_coverage"):
        st.caption(
            "Classes and modules aren’t drafted: "
            f"{coverage.get('classes_documented', 0)} of {coverage.get('classes', 0)} classes and "
            f"{coverage.get('files_with_module_docstring', 0)} of {coverage.get('file_count', 0)} files have one."
        )
        st.markdown(coverage_table(coverage))


PAGE_SIZE = 40


def row_key(fn: dict, seen: set) -> str:
    """
    A key unique within one run. The line number separates two definitions with the same
    name in one file (scrapy's Command.iterate_spider_output is defined twice), and component
    keys may not contain "__" (Spider.__init__), so runs of non-word characters collapse.
    """
    base = re.sub(r"[\W_]+", "_", f"{fn.get('file', '')}_{fn.get('lineno', '')}_{fn.get('name', '')}").strip("_")
    key, n = base, 1
    while key in seen:
        n += 1
        key = f"{base}_{n}"
    seen.add(key)
    return key


def _render_definition(fn: dict, key: str, diff_mode: bool = False) -> None:
    docstring = (fn.get("docstring") or "").strip()
    with st.container(key=f"docs_fn_{key}", gap="xxsmall"):
        with st.container(horizontal=True, vertical_alignment="center", gap="small"):
            st.markdown(f'<code class="docs-sig">{_literal(signature(fn))}</code>',
                        unsafe_allow_html=True, width="content")
            badge = status_badge(fn)
            if badge:
                st.badge(badge[0], color=badge[1])
        if diff_mode:
            change = function_diff(fn)
            if change:
                render_diff(*change, title=signature(fn), key=f"diff_inline_{key}")
                return
        if docstring:
            copy_text.docstring(docstring, key=f"doc_copy_{key}")
        elif fn.get("kind") == "class":
            st.caption("CodeDocAI drafts docstrings for functions and methods. A class summary is left to you.")
        else:
            st.caption("Neither our model nor the cloud fallback drafted this one.")
        # The diff is only worked out while the toggle is open; with thousands of functions,
        # building every one up front made each click wait on the whole list.
        source = st.expander("Source", type="compact", key=f"compact_src_{key}", on_change="rerun")
        if source.open:
            with source:
                change = function_diff(fn)
                if change:
                    render_diff(*change, title=signature(fn), key=f"diff_src_{key}", context=1000)
                else:
                    st.code(fn.get("source", ""), language="python")


def _show_more() -> None:
    st.session_state["docs_limit"] = st.session_state.get("docs_limit", PAGE_SIZE) + PAGE_SIZE


@st.fragment
def _render_function_list(everything: list) -> None:
    """Search and the state filter rerun only this list, not the page."""
    with st.container(horizontal=True, vertical_alignment="bottom", gap="small", key="docs_filters"):
        query = st.text_input("Search", key="docs_filter", placeholder="Name or file, e.g. spider.py")
        show_label = st.segmented_control("Show", list(SHOW_CHOICES), default="All", required=True,
                                          key="docs_filter_show")
        diff_mode = st.toggle("Diff view", key="docs_diff_mode",
                              help="Show each drafted docstring as the change it makes to the code.")
    matching = filter_definitions(everything, query, SHOW_CHOICES.get(show_label or "All", "Everything"))
    signature_now = (query, show_label, diff_mode)
    if st.session_state.get("_docs_view") != signature_now:
        st.session_state["_docs_view"] = signature_now
        st.session_state["docs_limit"] = PAGE_SIZE
    limit = st.session_state.get("docs_limit", PAGE_SIZE)
    functions = matching[:limit]
    if everything and not matching:
        st.info("Nothing matches this filter. Clear the search or choose All.")

    by_file: dict[str, list] = {}
    for fn in functions:
        by_file.setdefault(fn.get("file", "unknown"), []).append(fn)
    all_by_file: dict[str, list] = {}
    for fn in everything:
        all_by_file.setdefault(fn.get("file", "unknown"), []).append(fn)

    seen: set = set()
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
                _render_definition(fn, row_key(fn, seen), diff_mode)

    if matching:
        with st.container(horizontal=True, vertical_alignment="center", gap="small", key="docs_paging"):
            st.caption(f"Showing {len(functions):,} of {len(matching):,}"
                       + (f" (filtered from {len(everything):,})" if len(matching) != len(everything) else ""))
            if len(functions) < len(matching):
                st.button(f"Show {min(PAGE_SIZE, len(matching) - len(functions))} more", key="docs_more",
                          type="secondary", on_click=_show_more)


def render_documentation() -> None:
    if st.session_state.get("current_screen") != "docs":
        return

    heading, action = st.columns([4, 1], vertical_alignment="center")
    with heading:
        page_heading("Documentation")
    with action, st.container(horizontal=True, horizontal_alignment="right"):
        if st.session_state.get("pipeline_results") and st.button(
                "Ask a question", key="docs_ask_top", type="secondary", icon=":material/forum:"):
            st.session_state["current_screen"] = "qa"
            st.rerun()

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
