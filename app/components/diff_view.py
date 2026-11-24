"""
A before/after diff viewer for drafted docstrings: inserted lines tinted emerald
with a + gutter, warm syntax colours, line numbers, and a Copy button that puts
the patch on the clipboard.
"""

import difflib
import textwrap

import streamlit as st

from components._syntax import HIGHLIGHT_JS, SYNTAX_CSS

_HTML = """
<figure class="diff">
  <figcaption class="head">
    <span class="title"></span>
    <span class="stats"></span>
    <button type="button" class="copy" aria-live="polite">Copy</button>
  </figcaption>
  <div class="body" role="region" tabindex="0"><table><tbody></tbody></table></div>
  <div class="more" hidden></div>
</figure>
"""

_CSS = """
:host { display: block; }
.diff {
  margin: 0;
  border: 1px solid var(--border, #222222);
  border-radius: var(--radius-base, 8px);
  background: var(--surface-code, #121212);
  overflow: hidden;
  font-family: var(--font-mono, var(--st-code-font));
}
.head {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  border-bottom: 1px solid var(--border, #222222);
  font-size: 0.75rem;
  color: var(--text-muted, #A59C8A);
}
.title { color: var(--text-primary, #F0EAD9); }
.stats { flex: 1; }
.stats .add { color: var(--color-success, #4CAF50); }
.stats .del { color: var(--color-danger, #E5484D); margin-left: 8px; }
.copy {
  font: inherit;
  font-size: 0.75rem;
  color: var(--text-primary, #F0EAD9);
  background: transparent;
  border: 1px solid var(--border-strong, #5E5E5E);
  border-radius: var(--radius-sm, 4px);
  padding: 4px 10px;
  cursor: pointer;
  transition: border-color 150ms ease, color 150ms ease, scale 150ms ease-out;
}
.copy:focus-visible, .body:focus-visible { outline: 2px solid var(--accent-amber, #E8B339); outline-offset: 2px; }
.copy.done { border-color: var(--color-success, #4CAF50); color: var(--color-success, #4CAF50); }
@media (hover: hover) { .copy:hover { border-color: var(--accent-amber, #E8B339); color: var(--accent-amber, #E8B339); } }
@media (prefers-reduced-motion: no-preference) { .copy:active { scale: 0.96; } }
.body { overflow-x: auto; max-height: var(--diff-max-height, none); overflow-y: auto; }
table { border-collapse: collapse; width: 100%; font-size: 0.8125rem; line-height: 1.6; }
td { padding: 0 12px; white-space: pre; vertical-align: top; }
td.num {
  width: 1%;
  padding: 0 8px;
  text-align: right;
  color: var(--border-strong, #5E5E5E);
  user-select: none;
  font-variant-numeric: tabular-nums;
}
td.sign { width: 1%; padding: 0 4px 0 8px; user-select: none; color: var(--text-muted, #A59C8A); }
td.code { color: var(--text-primary, #F0EAD9); width: 100%; }
tr.add { background: rgba(76, 175, 80, 0.10); }
tr.add td.sign { color: var(--color-success, #4CAF50); }
tr.add td.num { color: var(--color-success, #4CAF50); box-shadow: inset 2px 0 0 var(--color-success, #4CAF50); }
tr.del { background: rgba(229, 72, 77, 0.10); }
tr.del td.sign { color: var(--color-danger, #E5484D); }
tr.hunk td { color: var(--text-muted, #A59C8A); background: var(--surface, #0A0A0A); padding-top: 2px; padding-bottom: 2px; }
.more { padding: 8px 12px; font-size: 0.75rem; color: var(--text-muted, #A59C8A); border-top: 1px solid var(--border, #222222); }
""" + SYNTAX_CSS

_JS = HIGHLIGHT_JS + """
export default function (component) {
  const { data, parentElement } = component
  const body = parentElement.querySelector("tbody")
  if (!body) return
  parentElement.querySelector(".title").textContent = data.title || ""
  const scroller = parentElement.querySelector(".body")
  scroller.setAttribute("aria-label", data.title || "Diff")
  if (data.max_height) scroller.style.setProperty("--diff-max-height", data.max_height + "px")
  const stats = parentElement.querySelector(".stats")
  stats.innerHTML = `<span class="add">+${data.added || 0}</span>` + (data.removed ? `<span class="del">-${data.removed}</span>` : "")

  body.replaceChildren()
  for (const line of data.lines || []) {
    const tr = document.createElement("tr")
    tr.className = line.t
    if (line.t === "hunk") {
      const td = document.createElement("td")
      td.colSpan = 4
      td.textContent = line.text
      tr.append(td)
    } else {
      const sign = line.t === "add" ? "+" : line.t === "del" ? "-" : " "
      tr.innerHTML = `<td class="num">${line.o ?? ""}</td><td class="num">${line.n ?? ""}</td>` +
        `<td class="sign">${sign}</td><td class="code">${highlightPython(line.text)}</td>`
    }
    body.append(tr)
  }
  const more = parentElement.querySelector(".more")
  more.hidden = !data.more
  more.textContent = data.more || ""

  const copy = parentElement.querySelector(".copy")
  copy.textContent = "Copy"
  copy.classList.remove("done")
  copy.onclick = async () => {
    const text = data.copy_text || ""
    let copied = false
    try {
      await navigator.clipboard.writeText(text)
      copied = true
    } catch (error) {
      // Clipboard API refused (no permission or no focus): fall back to a hidden textarea.
      const area = document.createElement("textarea")
      area.value = text
      area.setAttribute("readonly", "")
      area.style.position = "fixed"
      area.style.opacity = "0"
      document.body.append(area)
      area.select()
      try { copied = document.execCommand("copy") } catch (e) { copied = false }
      area.remove()
    }
    copy.textContent = copied ? "Copied" : "Copy failed"
    copy.classList.toggle("done", copied)
    clearTimeout(copy._timer)
    copy._timer = setTimeout(() => { copy.textContent = "Copy"; copy.classList.remove("done") }, 1600)
  }
}
"""

_DIFF = st.components.v2.component("codedocai_diff_view", html=_HTML, css=_CSS, js=_JS)

MAX_LINES = 600


def lines_from_patch(patch: str) -> list[dict]:
    """Rows for the viewer from a unified diff: hunk headers, context, added and removed lines."""
    rows, old_no, new_no = [], 0, 0
    for raw in patch.splitlines():
        if raw.startswith(("--- ", "+++ ")):
            rows.append({"t": "hunk", "text": raw})
        elif raw.startswith("@@"):
            numbers = raw.split("@@")[1].split()
            old_no = int(numbers[0][1:].split(",")[0]) if numbers else 0
            new_no = int(numbers[1][1:].split(",")[0]) if len(numbers) > 1 else 0
            rows.append({"t": "hunk", "text": raw})
        elif raw.startswith("+"):
            rows.append({"t": "add", "o": None, "n": new_no, "text": raw[1:]})
            new_no += 1
        elif raw.startswith("-"):
            rows.append({"t": "del", "o": old_no, "n": None, "text": raw[1:]})
            old_no += 1
        else:
            rows.append({"t": "ctx", "o": old_no, "n": new_no, "text": raw[1:] if raw.startswith(" ") else raw})
            old_no += 1
            new_no += 1
    return rows


def function_diff(fn: dict) -> tuple[str, str] | None:
    """(before, after) source of one function, with its drafted docstring written in the way the export writes it."""
    from backend.parser.extractor import extract_definitions
    from backend.writer import insert_docstrings

    docstring = (fn.get("docstring") or "").strip()
    if not fn.get("is_ai_draft") or not docstring:
        return None
    before = textwrap.dedent(fn.get("source") or "")
    try:
        definitions = extract_definitions(before, "snippet.py")
    except SyntaxError:
        return None
    for index, definition in enumerate(definitions):
        wanted = index == 0  # the snippet's own definition, not functions nested inside it
        definition["is_ai_draft"] = wanted
        if wanted:
            definition["docstring"] = docstring
    after = insert_docstrings(before, definitions)["source"]
    return (before, after) if after != before else None


def render_diff(before: str, after: str, *, title: str, key: str, context: int = 3) -> None:
    """A diff of two versions of one text."""
    patch = "".join(difflib.unified_diff(before.splitlines(keepends=True), after.splitlines(keepends=True),
                                         fromfile=f"a/{title}", tofile=f"b/{title}", n=context))
    render_patch(patch, title=title, key=key, show_file_headers=False)


def render_patch(patch: str, *, title: str, key: str, max_height: int | None = None,
                 show_file_headers: bool = True) -> None:
    """A unified diff (like docstrings.patch), with a Copy button for the whole patch."""
    rows = lines_from_patch(patch)
    if not show_file_headers:
        rows = [row for row in rows if not (row["t"] == "hunk" and row["text"].startswith(("--- ", "+++ ")))]
    added = sum(1 for row in rows if row["t"] == "add")
    removed = sum(1 for row in rows if row["t"] == "del")
    more = f"Showing {MAX_LINES} of {len(rows)} lines. Copy or export for the whole patch." if len(rows) > MAX_LINES else ""
    _DIFF(
        key=key,
        data={"title": title, "lines": rows[:MAX_LINES], "added": added, "removed": removed,
              "copy_text": patch, "more": more, "max_height": max_height},
        width="stretch",
    )
