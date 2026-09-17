"""
helpers.py -- CodeDocAI
Navigation rail, state reset, syntax highlighting, generation log builder,
and docs markdown builder.
"""

import html as _html
import math as _math
import re as _re
import time
import datetime

import streamlit as st
import streamlit.components.v1 as components

try:
    from fixtures import _FIXTURE_FUNCTIONS
except ImportError:
    from app.fixtures import _FIXTURE_FUNCTIONS

# ---------------------------------------------------------------------------
# Timing constants for the typewriter log -- kept in sync with JS.
# ---------------------------------------------------------------------------
_MS_PER_CHAR   = 16    # milliseconds typed per character
_PAUSE_PER_LINE = 200  # milliseconds pause after each line finishes


# ---------------------------------------------------------------------------
# Syntax highlighting
# ---------------------------------------------------------------------------
def _highlight_python(source_code: str) -> str:
    """
    Apply minimal syntax highlighting to Python source code using design tokens:
    - Keywords: --accent-amber (.code-kw)
    - Strings: --text-muted (.code-str)
    - Everything else: --text-primary
    HTML is escaped first to prevent injection.
    """
    escaped = _html.escape(source_code, quote=False)

    str_pattern = r'(f?"[^"\\]*(?:\\.[^"\\]*)*"|f?\'[^\'\\]*(?:\\.[^\'\\]*)*\')'
    kw_list = [
        "def", "return", "if", "for", "in", "global", "import", "from",
        "and", "or", "not", "False", "True", "None", "as", "with",
        "class", "elif", "else", "try", "except", "finally", "raise",
        "while", "break", "continue", "pass", "lambda", "is"
    ]
    kw_pattern = r'\b(' + '|'.join(kw_list) + r')\b'

    tokens = []
    last_idx = 0
    for match in _re.finditer(str_pattern, escaped):
        start, end = match.span()
        if start > last_idx:
            non_str = escaped[last_idx:start]
            highlighted_kw = _re.sub(kw_pattern, r'<span class="code-kw">\1</span>', non_str)
            tokens.append(highlighted_kw)
        str_val = match.group(0)
        tokens.append(f'<span class="code-str">{str_val}</span>')
        last_idx = end

    if last_idx < len(escaped):
        non_str = escaped[last_idx:]
        highlighted_kw = _re.sub(kw_pattern, r'<span class="code-kw">\1</span>', non_str)
        tokens.append(highlighted_kw)

    return "".join(tokens)


# ---------------------------------------------------------------------------
# State reset (Comprehensive Session Wipe)
# ---------------------------------------------------------------------------
def _reset_to_new_scan() -> None:
    """
    Completely purge all scan, pipeline, and RAG data from session state
    and navigate cleanly back to the Scan screen.
    """
    st.session_state["scan_status"] = "idle"
    st.session_state["scan_results"] = None
    st.session_state["scan_summary"] = None
    st.session_state["scan_error_message"] = None
    st.session_state["scan_github_url"] = ""
    st.session_state["repo_source"] = None
    st.session_state["repo_overview"] = None
    st.session_state["pipeline_results"] = None
    st.session_state["generation_attempt"] = 0
    st.session_state["generation_complete"] = False
    st.session_state["qa_chat_history"] = []
    st.session_state["current_screen"] = "scan"
    st.rerun()


# ---------------------------------------------------------------------------
# Navigation Rail
# ---------------------------------------------------------------------------
def render_nav_rail(current_screen: str) -> None:
    scan_status = st.session_state.get("scan_status", "idle")
    is_scan_populated = (scan_status == "populated")
    is_gen_complete = st.session_state.get("generation_complete", False)

    cols = st.columns(
        [2.5, 1.2, 0.3, 1.8, 0.3, 1.1, 0.3, 1.0, 0.3, 1.3],
        vertical_alignment="center",
    )

    with cols[0]:
        st.markdown('<div id="rail-wordmark"></div>', unsafe_allow_html=True)
        if st.button("CodeDocAI", key="rail_home"):
            st.session_state["current_screen"] = "landing"
            st.rerun()

    reachability = {
        "scan": True,
        "generation": is_scan_populated,
        "docs": is_gen_complete,
        "qa": is_gen_complete,
        "export": is_gen_complete,
    }

    steps = [
        ("scan",       "SCAN",     "rail_scan",     "rail-step-scan"),
        ("generation", "GENERATE", "rail_generate", "rail-step-generate"),
        ("docs",       "DOCS",     "rail_docs",     "rail-step-docs"),
        ("qa",         "Q&A",      "rail_qa",       "rail-step-qa"),
        ("export",     "EXPORT",   "rail_export",   "rail-step-export"),
    ]

    col_indices   = [1, 3, 5, 7, 9]
    arrow_indices = [2, 4, 6, 8]

    svg_chevron = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<polyline points="9 18 15 12 9 6"></polyline></svg>'
    )
    for arr_col_idx in arrow_indices:
        with cols[arr_col_idx]:
            st.markdown(f'<div class="rail-arrow">{svg_chevron}</div>', unsafe_allow_html=True)

    for i, (scr_key, label, btn_key, marker_id) in enumerate(steps):
        col = cols[col_indices[i]]
        with col:
            if current_screen == scr_key:
                st.markdown(f'<div class="rail-current">{label}</div>', unsafe_allow_html=True)
            elif reachability.get(scr_key, False):
                st.markdown(f'<div id="{marker_id}"></div>', unsafe_allow_html=True)
                if st.button(label, key=btn_key):
                    st.session_state["current_screen"] = scr_key
                    st.rerun()
            else:
                st.markdown(f'<div class="rail-muted">{label}</div>', unsafe_allow_html=True)

    st.markdown('<hr class="nav-rail-divider">', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Scan helpers
# ---------------------------------------------------------------------------
def _is_github_url(url: str) -> bool:
    u = url.strip().lower()
    return u.startswith("https://github.com/") or u.startswith("http://github.com/")


def _run_mock_scan(uploaded_file, github_url: str) -> None:
    try:
        from fixtures import _FIXTURE_DEFAULT, _FIXTURE_CLEAN
    except ImportError:
        from app.fixtures import _FIXTURE_DEFAULT, _FIXTURE_CLEAN

    if uploaded_file is None and github_url.strip() == "":
        st.session_state["scan_status"] = "error"
        st.session_state["scan_error_message"] = "Add a .zip file or a GitHub URL to scan."
        return

    if uploaded_file is None and not _is_github_url(github_url):
        st.session_state["scan_status"] = "error"
        st.session_state["scan_error_message"] = "That doesn't look like a valid GitHub URL."
        return

    with st.spinner("ANALYZING\u2026"):
        time.sleep(1.2)

    if uploaded_file is not None:
        fixture = _FIXTURE_DEFAULT
    else:
        url_lower = github_url.strip().lower()
        if "error" in url_lower:
            st.session_state["scan_status"] = "error"
            st.session_state["scan_error_message"] = (
                "Couldn't access this repository. Check the URL and try again."
            )
            return
        elif "empty" in url_lower:
            st.session_state["scan_status"] = "error"
            st.session_state["scan_error_message"] = (
                "No Python files found in this source. Try a different folder or repository."
            )
            return
        elif "clean" in url_lower:
            fixture = _FIXTURE_CLEAN
        else:
            fixture = _FIXTURE_DEFAULT

    file_count = len(fixture)
    missing_count = sum(row["missing"] for row in fixture)
    st.session_state["scan_status"] = "populated"
    st.session_state["scan_error_message"] = None
    st.session_state["scan_results"] = fixture
    st.session_state["scan_summary"] = {
        "file_count": file_count,
        "missing_count": missing_count,
    }


# ---------------------------------------------------------------------------
# Generation log builder
# ---------------------------------------------------------------------------
def _build_generation_log(scan_results: list, rate_limited: bool) -> tuple:
    AMBER = "#FFD700"
    RED   = "#E5484D"
    MUTED = "#9CA3AF"

    lines = []
    for row in scan_results:
        path    = row["path"]
        missing = row["missing"]
        if missing > 0:
            plural = "s" if missing != 1 else ""
            text   = f"{path} \u2014 drafting {missing} docstring{plural}... done"
            color  = AMBER
        else:
            text  = f"{path} \u2014 already documented, skipping"
            color = MUTED
        lines.append((text, color))

    if rate_limited:
        lines.append(("synthesizing module overview... rate limit reached", RED))
    else:
        lines.append(("synthesizing module overview... done", AMBER))
        lines.append(("indexing for Q&A... done", AMBER))

    total_chars = sum(len(t) for t, _ in lines)
    total_ms    = total_chars * _MS_PER_CHAR + len(lines) * _PAUSE_PER_LINE
    duration_s  = total_ms / 1000.0

    return lines, duration_s


def _build_log_component(lines: list, height: int = 340) -> str:
    js_lines = "[\n"
    for text, color in lines:
        safe_text  = text.replace("\\", "\\\\").replace("'", "\\'")
        safe_color = color if color else "#A59C8A"
        js_lines  += f"    {{text: '{safe_text}', color: '{safe_color}'}},\n"
    js_lines += "  ]"

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{
    background: transparent;
    font-family: 'IBM Plex Mono', 'Courier New', monospace;
    font-feature-settings: 'liga' 0, 'calt' 0;
    font-variant-ligatures: none;
  }}
  #log {{
    display: flex;
    flex-direction: column;
    gap: 6px;
    width: 100%;
  }}
  .log-line {{
    font-size: 0.8rem;
    font-weight: 400;
    line-height: 1.5;
    opacity: 0;
    transition: opacity 0.1s ease;
    white-space: pre-wrap;
    word-break: break-all;
  }}
  .log-line.visible {{ opacity: 1; }}
  .cursor {{
    display: inline-block;
    width: 7px;
    height: 1em;
    background: #E8B339;
    vertical-align: text-bottom;
    animation: blink 0.8s step-end infinite;
    margin-left: 1px;
  }}
  @keyframes blink {{
    0%, 100% {{ opacity: 1; }}
    50%       {{ opacity: 0; }}
  }}
</style>
</head>
<body>
<div id="log"></div>
<script>
(function() {{
  var MS_PER_CHAR  = {_MS_PER_CHAR};
  var PAUSE_PER_LINE = {_PAUSE_PER_LINE};
  var lines = {js_lines};
  var logEl = document.getElementById('log');
  var lineIndex = 0;
  var charIndex = 0;
  var currentEl = null;
  var cursorEl  = null;

  function nextLine() {{
    if (lineIndex >= lines.length) return;
    var item = lines[lineIndex];
    currentEl = document.createElement('div');
    currentEl.className = 'log-line visible';
    currentEl.style.color = item.color;
    cursorEl = document.createElement('span');
    cursorEl.className = 'cursor';
    currentEl.appendChild(cursorEl);
    logEl.appendChild(currentEl);
    charIndex = 0;
    typeChar();
  }}

  function typeChar() {{
    var item = lines[lineIndex];
    if (charIndex < item.text.length) {{
      var node = document.createTextNode(item.text[charIndex]);
      currentEl.insertBefore(node, cursorEl);
      charIndex++;
      setTimeout(typeChar, MS_PER_CHAR);
    }} else {{
      if (cursorEl && cursorEl.parentNode) cursorEl.parentNode.removeChild(cursorEl);
      lineIndex++;
      if (lineIndex < lines.length) setTimeout(nextLine, PAUSE_PER_LINE);
    }}
  }}

  nextLine();
}})();
</script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Docs Markdown Builder (Defensive Key Parsing)
# ---------------------------------------------------------------------------
def _build_docs_markdown(pipeline_results: dict = None, scan_summary: dict = None) -> str:
    """Compiles the generated pipeline documentation payload into formatted Markdown."""
    lines = []
    
    current_utc = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    lines.append("# CodeDocAI Generated Documentation")
    lines.append(f"*Generated on: {current_utc} UTC*\n")
    lines.append("---\n")
    
    if not pipeline_results:
        pipeline_results = st.session_state.get("pipeline_results") or {}
        
    overview = pipeline_results.get("overview", "No architecture overview generated.")
    lines.append(overview)
    lines.append("\n---\n")
    lines.append("## Module Documentation\n")
    
    functions = pipeline_results.get("functions", [])
    files_dict = {}
    for fn in functions:
        # Fallback hierarchy to prevent "unknown_file.py"
        file_name = fn.get("file") or fn.get("file_path") or fn.get("path") or "unknown_file.py"
        files_dict.setdefault(file_name, []).append(fn)
        
    for file_name, funcs in files_dict.items():
        lines.append(f"### File: `{file_name}`")
        for fn in funcs:
            fn_name = fn.get("name", fn.get("function", "unknown_function"))
            docstring = fn.get("docstring", "No docstring available.")
            source = fn.get("source", fn.get("code", ""))
            
            lines.append(f"#### `def {fn_name}()`")
            lines.append("**Description & Parameters:**")
            lines.append(f"```python\n{docstring}\n```")
            lines.append("**Source Code:**")
            lines.append("<details><summary>Click to expand</summary>\n")
            lines.append(f"```python\n{source}\n```\n")
            lines.append("</details>\n")
        lines.append("---\n")
        
    return "\n".join(lines)