"""
helpers.py -- CodeDocAI
Top bar, state reset, Markdown rendering for answers, docs markdown
builder, and the audit logger.
"""

import datetime
import html as _html
import logging
import re as _re
from pathlib import Path

import streamlit as st

from backend.storage import read_json, update_json

logger = logging.getLogger(__name__)

_ROOT_DIR = Path(__file__).resolve().parents[1]
_AUDIT_FILE = _ROOT_DIR / "enterprise_audit.json"


# ---------------------------------------------------------------------------
# State reset (Comprehensive Session Wipe)
# ---------------------------------------------------------------------------
def collection_name_for(session_id: str) -> str:
    """Name of the ChromaDB collection that belongs to a browser session."""
    return f"codedocai_{session_id}"


def session_collection_name() -> str:
    """Name of the ChromaDB collection that belongs to this browser session."""
    return collection_name_for(st.session_state.get("session_id", "default"))


def _reset_to_new_scan() -> None:
    """
    Completely purge all scan, pipeline, and RAG data from session state,
    delete the scanned source copy and this session’s vector index,
    and navigate cleanly back to the Scan screen.
    """
    from backend.rag.vectorstore import reset_collection
    from backend.repo.loader import cleanup_repo

    cleanup_repo((st.session_state.get("repo_source") or {}).get("local_path"))
    if st.session_state.get("generation_complete") or st.session_state.get("pipeline_results"):
        reset_collection(session_collection_name())

    st.session_state["overview_context"] = None
    st.session_state["overview_error"] = None
    st.session_state["qa_answer_cache"] = {}
    st.session_state["_confirm_new_scan"] = None
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


DISCARD_LABEL = "Discard scan"


def new_scan_pending(key: str) -> bool:
    """True while this button’s confirmation dialog is open."""
    return st.session_state.get("_confirm_new_scan") == key


def _close_new_scan_dialog() -> None:
    st.session_state["_confirm_new_scan"] = None


@st.dialog("Discard this scan?", on_dismiss=_close_new_scan_dialog)
def _new_scan_dialog(key: str) -> None:
    st.markdown(
        '<p class="dialog-body">Its documentation, search index and Q&amp;A history are deleted. '
        "Export first to keep them.</p>",
        unsafe_allow_html=True,
    )
    with st.container(horizontal=True, horizontal_alignment="right", gap="small", key=f"{key}_confirm_row"):
        if st.button("Cancel", key=f"{key}_cancel", type="secondary"):
            _close_new_scan_dialog()
            st.rerun()
        # The danger_* key gives this button the danger colour instead of the brand accent.
        if st.button(DISCARD_LABEL, key=f"danger_{key}_confirm", type="primary"):
            _close_new_scan_dialog()
            _reset_to_new_scan()


def new_scan_button(label: str, key: str, **button_kwargs) -> None:
    """
    A "new scan" button that asks before throwing work away.

    Starting a new scan deletes the generated documentation, the vector index and
    the Q&A history of this session, and it cannot be undone. When the session
    holds any of that, the first click opens a confirmation dialog; the reset
    happens on the explicit confirmation. With nothing to lose, it resets at once.
    The dialog is opened from session state, so it stays open across reruns until
    it is answered or dismissed.
    """
    has_work = bool(
        st.session_state.get("generation_complete")
        or st.session_state.get("pipeline_results")
        or st.session_state.get("qa_chat_history")
    )
    if st.button(label, key=key, **button_kwargs):
        if has_work:
            st.session_state["_confirm_new_scan"] = key
        else:
            _reset_to_new_scan()
    if new_scan_pending(key):
        _new_scan_dialog(key)


# ---------------------------------------------------------------------------
# Stats and toasts
# ---------------------------------------------------------------------------
def render_stats(items: list[tuple[str, object]], key: str | None = None, count_up: bool = False) -> None:
    """
    One row of figures in the shared stat style: the value in tabular mono, the
    label under it in muted sentence case. items holds (label, value) pairs; a
    third element, when present, is a short note shown after the label.
    """
    cells = []
    for item in items:
        label, value = item[0], item[1]
        note = f'<span class="stat-note">{_html.escape(str(item[2]))}</span>' if len(item) > 2 and item[2] else ""
        cells.append(
            '<div class="stat">'
            f'<span class="stat-value">{_html.escape(str(value))}</span>'
            f'<span class="stat-label">{_html.escape(label)}{note}</span>'
            '</div>'
        )
    row_class = "stat-row count-up" if count_up else "stat-row"
    html_text = f'<div class="{row_class}" role="list">{"".join(cells)}</div>'.replace('<div class="stat">', '<div class="stat" role="listitem">')
    if key:
        with st.container(key=key):
            st.markdown(html_text, unsafe_allow_html=True)
    else:
        st.markdown(html_text, unsafe_allow_html=True)


# One page-level script for the effects that need JavaScript: count-up figures and the
# spotlight that follows the pointer across cards. It installs itself once per page.
_FX_SCRIPT = r"""
<script>(function () {
  var w = window.parent || window, doc = w.document;
  if (w.__codedocaiFx) { w.__codedocaiFx.scan(); return; }
  var still = w.matchMedia('(prefers-reduced-motion: reduce)').matches;
  // The index loader's ring fill animates as a percentage (see styles.py, .ixl-ring).
  // \x3c and \x3e are angle brackets: written literally, the tag-like syntax string got the whole
  // script stripped on its way into the page (so do not write them literally anywhere in here).
  try { w.CSS.registerProperty({ name: '--ixl-p', syntax: '\x3cpercentage\x3e', inherits: false, initialValue: '0%' }); } catch (e) {}
  // The figure's own text node is edited in place, never replaced: React keeps a reference to
  // that node, and when the next screen reuses the element it writes the new value into it.
  // Setting textContent swapped in a new node, so the old figures stayed on the next screen.
  function countUp(el) {
    if (el.dataset.counted) return;
    el.dataset.counted = '1';
    var node = el.firstChild;
    if (still || !node || node.nodeType !== 3 || node.nextSibling) return;
    var text = node.nodeValue, parts = text.split(/(\d+)/), last = text;
    if (parts.length < 2) return;
    var start = null, ms = 700;
    function frame(t) {
      if (node.nodeValue !== last) return;  // React rendered a new value: leave it alone
      if (start === null) start = t;
      var k = Math.min((t - start) / ms, 1), e = 1 - Math.pow(1 - k, 3);
      last = k < 1 ? parts.map(function (p) { return /^\d+$/.test(p) ? String(Math.round(parseInt(p, 10) * e)) : p; }).join('') : text;
      node.nodeValue = last;
      if (k < 1) w.requestAnimationFrame(frame);
    }
    w.requestAnimationFrame(frame);
  }
  var REVEAL = '.home-reveal, .st-key-tryit, .st-key-how_tour, .closing-section, .st-key-closing_cta';
  var seen = new w.IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      // On the landing page, whatever is already on screen waits for the hero to finish.
      var wait = doc.querySelector('.hero-word') ? Math.max(0, 3500 - (w.performance.now() - (w.__codedocaiHeroStart || 0))) : 0;
      var stagger = parseInt(entry.target.style.getPropertyValue('--reveal-delay'), 10) || 0;
      entry.target.style.setProperty('--reveal-delay', (wait + stagger) + 'ms');
      entry.target.classList.add('revealed');
      // Figures inside a revealed section count up once the section has faded in.
      entry.target.querySelectorAll('.count-up .stat-value').forEach(function (el) {
        w.setTimeout(function () { countUp(el); }, wait + stagger + 200);
      });
      seen.unobserve(entry.target);
    });
  }, { threshold: 0.15 });
  function reveal() {
    if (still) return;
    if (doc.querySelector('.hero-word') && !w.__codedocaiHeroStart) w.__codedocaiHeroStart = w.performance.now();
    if (!doc.querySelector('.hero-word')) w.__codedocaiHeroStart = 0;
    doc.documentElement.classList.add('fx-reveal');
    doc.querySelectorAll(REVEAL).forEach(function (el, i) {
      if (el.dataset.revealWatched) return;
      el.dataset.revealWatched = '1';
      var siblings = el.parentElement ? [].indexOf.call(el.parentElement.children, el) : 0;
      el.style.setProperty('--reveal-delay', Math.min(siblings, 4) * 90 + 'ms');
      seen.observe(el);
    });
  }
  // Live logs (the Generate screen's Details) follow the newest line, unless the
  // reader has scrolled up to look at something; scrolling back down resumes it.
  function pinLogs() {
    doc.querySelectorAll('.st-key-compact_gen_details [data-testid="stCode"] *, .st-key-scan_status [data-testid="stExpanderDetails"]').forEach(function (el) {
      if (el.scrollHeight <= el.clientHeight + 2) return;
      if (!el.dataset.pinWatched) {
        el.dataset.pinWatched = '1';
        el.addEventListener('scroll', function () {
          el.dataset.pinned = el.scrollHeight - el.scrollTop - el.clientHeight < 40 ? '1' : '0';
        }, { passive: true });
      }
      if (el.dataset.pinned !== '0') el.scrollTop = el.scrollHeight;
    });
  }
  function scan() {
    pinLogs();
    doc.querySelectorAll('.count-up .stat-value').forEach(function (el) { if (still || !el.closest('.home-reveal')) countUp(el); });
    reveal();
  }
  doc.addEventListener('pointermove', function (ev) {
    var card = ev.target.closest && ev.target.closest('.spotlight, [class*="st-key-docs_file_"], .home-card');
    if (!card) return;
    var r = card.getBoundingClientRect();
    card.style.setProperty('--spot-x', (ev.clientX - r.left) + 'px');
    card.style.setProperty('--spot-y', (ev.clientY - r.top) + 'px');
  }, { passive: true });
  new w.MutationObserver(scan).observe(doc.body, { childList: true, subtree: true });
  w.__codedocaiFx = { scan: scan };
  scan();
})();</script>
"""


def install_effects() -> None:
    """Mounts the page-level effects script in a hidden container (it takes no space)."""
    with st.container(key="fx_scripts"):
        st.html(_FX_SCRIPT, unsafe_allow_javascript=True)


def skeleton(lines: int = 3, *, key: str | None = None):
    """
    Grey placeholder bars for content that is on its way. Returns the st.empty slot,
    so the caller can clear it when the real content arrives. Shimmers only when the
    visitor allows motion.
    """
    widths = [92, 78, 85, 64, 88, 72]
    bars = "".join(f'<span class="skeleton-bar" style="width:{widths[i % len(widths)]}%"></span>' for i in range(lines))
    slot = st.empty()
    slot.markdown(f'<div class="skeleton" role="status" aria-label="Loading">{bars}</div>', unsafe_allow_html=True)
    return slot


def queue_toast(message: str, icon: str = ":material/check_circle:") -> None:
    """A toast shown on the next run; use it before st.rerun(), which would drop one shown now."""
    st.session_state.setdefault("_toasts", []).append((message, icon))


def show_queued_toasts() -> None:
    for message, icon in st.session_state.pop("_toasts", []):
        st.toast(message, icon=icon)


# ---------------------------------------------------------------------------
# Top bar and page headings
# ---------------------------------------------------------------------------
def render_top_bar(current_screen: str, offline: str | None = None) -> None:
    """
    The sticky, frosted header every screen shares (an inline component), with the
    command palette mounted beside it. Clicks are handled in callbacks before the
    screen renders. It replaces the sidebar, so signing in and out happens here.
    """
    from components import command_palette, topbar

    with st.container(key="topbar_wrap"):
        topbar.render(current_screen, offline=offline)
        command_palette.render(current_screen)


def page_heading(title: str, subtitle: str | None = None) -> None:
    """The screen's real h1, with an optional one-line subtitle under it."""
    html_text = f'<h1 class="page-h1">{_html.escape(title)}</h1>'
    if subtitle:
        html_text += f'<p class="page-sub">{_html.escape(subtitle)}</p>'
    st.markdown(html_text, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Markdown rendering for Q&A answers
# ---------------------------------------------------------------------------
def _inline_markdown(text: str) -> str:
    """Escapes the text, then renders `code`, **bold** and *italic*."""
    rendered = []
    for part in _re.split(r"(`[^`]+`)", _html.escape(text, quote=False)):
        if len(part) > 2 and part.startswith("`") and part.endswith("`"):
            rendered.append(f"<code>{part[1:-1]}</code>")
        else:
            part = _re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", part)
            part = _re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", part)
            rendered.append(part)
    return "".join(rendered)


def markdown_to_html(text: str) -> str:
    """
    Renders the Markdown a model typically writes in an answer: paragraphs, headings,
    bullet and numbered lists, fenced code blocks, `code`, **bold** and *italic*.

    Everything is HTML-escaped first, so text from the model or the scanned code can
    never inject markup. The result contains no line breaks: it is embedded in a
    larger HTML block, where a blank line would end that block early.
    """
    blocks = []
    paragraph = []
    items = []
    list_tag = None
    code_lines = None

    def flush_paragraph():
        if paragraph:
            blocks.append(("p", "<br>".join(_inline_markdown(line) for line in paragraph)))
            paragraph.clear()

    def flush_list():
        nonlocal list_tag
        if items:
            body = "".join(f"<li>{_inline_markdown(item)}</li>" for item in items)
            blocks.append((list_tag, f"<{list_tag}>{body}</{list_tag}>"))
            items.clear()
        list_tag = None

    def flush_code():
        nonlocal code_lines
        if code_lines is not None:
            body = "&#10;".join(_html.escape(line, quote=False) for line in code_lines)
            blocks.append(("pre", f"<pre><code>{body}</code></pre>"))
        code_lines = None

    for line in (text or "").splitlines():
        stripped = line.strip()

        if stripped.startswith("```"):
            if code_lines is None:
                flush_paragraph()
                flush_list()
                code_lines = []
            else:
                flush_code()
            continue
        if code_lines is not None:
            code_lines.append(line)
            continue

        if not stripped:
            flush_paragraph()
            flush_list()
            continue

        heading = _re.match(r"#{1,6}\s+(.*)", stripped)
        bullet = _re.match(r"[-*+]\s+(.*)", stripped)
        numbered = _re.match(r"\d+[.)]\s+(.*)", stripped)

        if heading:
            flush_paragraph()
            flush_list()
            blocks.append(("h", f"<p><b>{_inline_markdown(heading.group(1))}</b></p>"))
        elif bullet or numbered:
            flush_paragraph()
            wanted = "ul" if bullet else "ol"
            if list_tag and list_tag != wanted:
                flush_list()
            list_tag = wanted
            items.append((bullet or numbered).group(1))
        else:
            flush_list()
            paragraph.append(stripped)

    flush_code()
    flush_paragraph()
    flush_list()

    if len(blocks) == 1 and blocks[0][0] == "p":
        return blocks[0][1]  # a plain one-paragraph answer needs no wrapper
    return "".join(f"<p>{body}</p>" if kind == "p" else body for kind, body in blocks)


# ---------------------------------------------------------------------------
# Docs Markdown Builder (Defensive Key Parsing)
# ---------------------------------------------------------------------------
def _build_docs_markdown(pipeline_results: dict | None = None, scan_summary: dict | None = None) -> str:
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
            docstring = fn.get("docstring") or "No docstring available."
            source = fn.get("source", fn.get("code", ""))

            if fn.get("kind") == "class":
                lines.append(f"#### `class {fn_name}`")
            else:
                lines.append(f"#### `def {fn_name}()`")
            lines.append("**Docstring:**")
            lines.append(f"```python\n{docstring}\n```")
            lines.append("**Source Code:**")
            lines.append("<details><summary>Show source</summary>\n")
            lines.append(f"```python\n{source}\n```\n")
            lines.append("</details>\n")
        lines.append("---\n")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Audit log (demo)
# ---------------------------------------------------------------------------
MAX_AUDIT_ENTRIES = 5000  # oldest entries are dropped past this, so the file can't grow forever


def read_audit_log() -> list[dict]:
    """Every entry in the audit ledger, oldest first. Empty if the file is missing or unreadable."""
    return read_json(_AUDIT_FILE, [])


def purge_audit_log(user: str | None = None) -> int:
    """Deletes every entry, or every entry of one user. Returns how many were deleted."""
    deleted = 0

    def purge(logs: list[dict]) -> list[dict]:
        nonlocal deleted
        kept = [] if user is None else [log for log in logs if log.get("user") != user]
        deleted = len(logs) - len(kept)
        return kept

    update_json(_AUDIT_FILE, purge, [])
    return deleted


def log_audit(action: str, details: str, user: str, severity: str = "INFO") -> None:
    """Adds a UTC-timestamped entry to the demo audit log."""
    entry = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "user": user,
        "action": action,
        "severity": severity,
        "details": details,
    }
    update_json(_AUDIT_FILE, lambda logs: [*logs, entry][-MAX_AUDIT_ENTRIES:], [])


def audit_event(action: str, details: str, severity: str = "INFO") -> None:
    """
    Records an action of the signed-in developer in the audit ledger.
    Does nothing for anonymous use or for the manager, who is the auditor.
    """
    if st.session_state.get("authenticated") and st.session_state.get("role") == "developer":
        log_audit(action, details, st.session_state.get("username"), severity=severity)
