"""
helpers.py -- CodeDocAI
Navigation rail, state reset, syntax highlighting, generation log builder,
and docs markdown builder.
"""

import html as _html
import math as _math
import re as _re
import time

import streamlit as st
import streamlit.components.v1 as components

try:
    from fixtures import _FIXTURE_FUNCTIONS
except ImportError:
    from app.fixtures import _FIXTURE_FUNCTIONS

# ---------------------------------------------------------------------------
# Timing constants for the typewriter log -- kept in sync with JS.
# Changing either value here MUST be reflected in _build_log_component().
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

    # Match double and single quoted strings, including f-strings
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
# State reset
# ---------------------------------------------------------------------------
def _reset_to_new_scan() -> None:
    """
    Reset scan and generation state to defaults and navigate to Scan screen.
    """
    st.session_state["scan_status"] = "idle"
    st.session_state["scan_results"] = None
    st.session_state["scan_summary"] = None
    st.session_state["scan_error_message"] = None
    st.session_state["generation_attempt"] = 0
    st.session_state["generation_complete"] = False
    st.session_state["qa_chat_history"] = []
    st.session_state["current_screen"] = "scan"
    st.rerun()


# ---------------------------------------------------------------------------
# Navigation Rail
# ---------------------------------------------------------------------------
def render_nav_rail(current_screen: str) -> None:
    """
    Shared top navigation rail for Scan, Generation, Docs, Q&A, and Export screens.
    Renders wordmark on the left and breadcrumb steps on the right.

    Gating (Session 6a-fix + Session 7):
    - SCAN: always reachable
    - GENERATE: reachable only when scan_status == 'populated'
    - DOCS, Q&A, EXPORT: reachable only when generation_complete == True
    """
    scan_status = st.session_state.get("scan_status", "idle")
    is_scan_populated = (scan_status == "populated")
    is_gen_complete = st.session_state.get("generation_complete", False)

    # 10 columns: Wordmark, Step1, Arr1, Step2, Arr2, Step3, Arr3, Step4, Arr4, Step5
    # Proportions sized so no label wraps; white-space:nowrap enforced in CSS.
    cols = st.columns(
        [2.5, 1.2, 0.3, 1.8, 0.3, 1.1, 0.3, 1.0, 0.3, 1.3],
        vertical_alignment="center",
    )

    # 1. Wordmark -> returns to landing
    with cols[0]:
        st.markdown('<div id="rail-wordmark"></div>', unsafe_allow_html=True)
        if st.button("CodeDocAI", key="rail_home"):
            st.session_state["current_screen"] = "landing"
            st.rerun()

    # Step reachability map
    reachability = {
        "scan": True,
        "generation": is_scan_populated,
        "docs": is_gen_complete,
        "qa": is_gen_complete,
        "export": is_gen_complete,
    }

    # Step definitions: (screen_key, display_label, button_key, marker_id)
    steps = [
        ("scan",       "SCAN",     "rail_scan",     "rail-step-scan"),
        ("generation", "GENERATE", "rail_generate", "rail-step-generate"),
        ("docs",       "DOCS",     "rail_docs",     "rail-step-docs"),
        ("qa",         "Q&A",      "rail_qa",       "rail-step-qa"),
        ("export",     "EXPORT",   "rail_export",   "rail-step-export"),
    ]

    col_indices   = [1, 3, 5, 7, 9]
    arrow_indices = [2, 4, 6, 8]

    # Render arrows (using inline SVG for perfect vertical centering)
    svg_chevron = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<polyline points="9 18 15 12 9 6"></polyline></svg>'
    )
    for arr_col_idx in arrow_indices:
        with cols[arr_col_idx]:
            st.markdown(f'<div class="rail-arrow">{svg_chevron}</div>', unsafe_allow_html=True)

    # Render steps
    for i, (scr_key, label, btn_key, marker_id) in enumerate(steps):
        col = cols[col_indices[i]]
        with col:
            if current_screen == scr_key:
                # Current step -- bold/underlined amber, non-clickable
                st.markdown(f'<div class="rail-current">{label}</div>', unsafe_allow_html=True)
            elif reachability.get(scr_key, False):
                # Reachable step -- button styled as breadcrumb link
                st.markdown(f'<div id="{marker_id}"></div>', unsafe_allow_html=True)
                if st.button(label, key=btn_key):
                    st.session_state["current_screen"] = scr_key
                    st.rerun()
            else:
                # Unreachable step -- inert muted text
                st.markdown(f'<div class="rail-muted">{label}</div>', unsafe_allow_html=True)

    st.markdown('<hr class="nav-rail-divider">', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Scan helpers
# ---------------------------------------------------------------------------
def _is_github_url(url: str) -> bool:
    """Return True if url looks like a plausible GitHub URL."""
    u = url.strip().lower()
    return u.startswith("https://github.com/") or u.startswith("http://github.com/")


def _run_mock_scan(uploaded_file, github_url: str) -> None:
    """
    Validate inputs, run mock scan (with spinner), write results to session_state.
    Priority: uploaded file > github_url.
    """
    from fixtures import _FIXTURE_DEFAULT, _FIXTURE_CLEAN

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
    """
    Build the list of log lines and the expected total animation duration.

    Returns:
        lines      -- list of (text:str, color:str) tuples
        duration_s -- float seconds Python should sleep before showing outcome
    """
    AMBER = "#FFD700"
    RED   = "#E5484D"
    MUTED = "#9CA3AF"

    lines = []

    # Per-file drafting lines  (derived from scan_results, never hardcoded)
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

    # Synthesize line -- always present; color/wording differs by outcome
    if rate_limited:
        lines.append(("synthesizing module overview... rate limit reached", RED))
        # No index line follows when rate-limited
    else:
        lines.append(("synthesizing module overview... done", AMBER))
        lines.append(("indexing for Q&A... done", AMBER))

    # Approximate total animation duration (matches JS timing constants)
    total_chars = sum(len(t) for t, _ in lines)
    total_ms    = total_chars * _MS_PER_CHAR + len(lines) * _PAUSE_PER_LINE
    duration_s  = total_ms / 1000.0

    return lines, duration_s


def _build_log_component(lines: list, height: int = 340) -> str:
    """
    Build the self-contained HTML/JS string for the typewriter log.
    Rendered via components.v1.html() so <script> actually executes.

    Timing constants (_MS_PER_CHAR, _PAUSE_PER_LINE) must stay in sync
    with the module-level values above.
    """
    # Serialize lines as a JS array literal
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
    background: transparent; /* Let the iframe be invisible */
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
# Docs markdown builder
# ---------------------------------------------------------------------------
def _build_docs_markdown(scan_results: list, scan_summary: dict) -> str:
    """
    Build the full markdown string for the download button.
    Derived entirely from scan_results + _FIXTURE_FUNCTIONS -- never hardcoded.
    """
    lines = ["# CodeDocAI \u2014 Generated Documentation\n"]
    missing_count = scan_summary.get("missing_count", 0) if scan_summary else 0

    if missing_count == 0:
        lines.append(
            "_Codebase fully documented \u2014 0 missing docstrings detected._\n"
        )
        for row in (scan_results or []):
            lines.append(f"- `{row['path']}` \u2014 already documented.\n")
        return "\n".join(lines)

    for row in (scan_results or []):
        path    = row["path"]
        missing = row["missing"]
        funcs   = row["functions"]

        lines.append(f"\n---\n\n## `{path}`\n")

        if missing == 0:
            lines.append(f"_{path} \u2014 already documented._\n")
            continue

        # File has missing functions -- use fixture data
        file_data = _FIXTURE_FUNCTIONS.get(path)
        if file_data is None:
            lines.append("_Documentation drafted for this file._\n")
            continue

        module_summary = file_data["module_summary"]
        overview = (
            f"{module_summary} {missing} of its {funcs} functions shipped "
            f"without docstrings; each is drafted below from its implementation."
        )
        lines.append(f"{overview}\n")

        for fn in file_data["functions"]:
            lines.append(f"\n### `{fn['name']}` _(ai draft)_\n")
            lines.append(f"**Docstring:**\n\n> {fn['docstring']}\n")
            lines.append(f"\n**Source:**\n\n```python\n{fn['source']}\n```\n")

    return "\n".join(lines)
