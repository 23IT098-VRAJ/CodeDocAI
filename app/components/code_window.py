"""
The landing page's editor window: real, indented Python from the Spider sample,
with the drafted docstring typed in once. Under prefers-reduced-motion the
finished code shows straight away.
"""

import streamlit as st

from components._syntax import HIGHLIGHT_JS, SYNTAX_CSS

# Line 4 is the docstring the window "drafts"; every other line is shown as is.
SAMPLE = [
    "class Spider:",
    "    @staticmethod",
    "    def crawl_page(thread_name, page_url):",
    '        """Crawl a single page."""',  # CodeT5's own draft in the sample run
    "        if page_url not in Spider.crawled:",
    "            Spider.gather_links(page_url)",
    "            Spider.crawled.add(page_url)",
]
DOCSTRING_LINE = 3

_HTML = """
<figure class="window" aria-label="spider.py with a drafted docstring">
  <figcaption class="chrome">
    <span class="dots" aria-hidden="true"><i></i><i></i><i></i></span>
    <span class="tab">spider.py</span>
    <span class="state" aria-live="polite"></span>
  </figcaption>
  <pre class="code" aria-hidden="true"></pre>
  <p class="sr-only"></p>
</figure>
"""

_CSS = """
:host { display: block; }
.window {
  margin: 0;
  background: var(--surface, #0A0A0A);
  border: 1px solid var(--border, #222222);
  border-radius: var(--radius-lg, 16px);
  overflow: hidden;
  font-family: var(--font-mono, var(--st-code-font));
}
.chrome {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  background: var(--surface-sunken, #050505);
  border-bottom: 1px solid var(--border, #222222);
  font-size: 0.75rem;
}
.dots { display: inline-flex; gap: 6px; }
.dots i { width: 10px; height: 10px; border-radius: 999px; background: var(--border-strong, #5E5E5E); opacity: 0.6; }
.tab {
  color: var(--text-primary, #F0EAD9);
  padding: 2px 10px;
  border-radius: var(--radius-sm, 4px);
  background: var(--surface-raised, #111111);
  box-shadow: inset 0 -2px 0 var(--accent-amber, #E8B339);
}
.state { margin-left: auto; color: var(--text-muted, #A59C8A); }
.state.done { color: var(--color-success, #4CAF50); }
.code {
  margin: 0;
  padding: 14px 0;
  font-family: inherit;
  font-size: 0.8125rem;
  line-height: 1.7;
  color: var(--text-primary, #F0EAD9);
  overflow-x: auto;
}
.line { display: block; padding: 0 16px 0 0; white-space: pre; }
.line.drafted { background: rgba(76, 175, 80, 0.10); box-shadow: inset 2px 0 0 var(--color-success, #4CAF50); }
.no { display: inline-block; width: 3ch; margin-right: 16px; text-align: right; color: var(--border-strong, #5E5E5E); user-select: none; }
.caret { display: inline-block; width: 1px; height: 1.1em; vertical-align: text-bottom; background: var(--accent-amber, #E8B339); }
@media (prefers-reduced-motion: no-preference) {
  .caret { animation: blink 1s steps(1) infinite; }
}
@keyframes blink { 50% { opacity: 0; } }
.sr-only { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }
""" + SYNTAX_CSS

_JS = HIGHLIGHT_JS + """
export default function (component) {
  const { data, parentElement } = component
  const pre = parentElement.querySelector(".code")
  const state = parentElement.querySelector(".state")
  if (!pre || !state) return
  const lines = data.lines || []
  const target = data.docstring_line
  parentElement.querySelector(".sr-only").textContent = lines.join("\\n")

  const draw = (typed, done) => {
    pre.innerHTML = lines.map((line, i) => {
      const text = i === target ? line.slice(0, typed) : line
      const caret = i === target && !done ? '<span class="caret"></span>' : ""
      const cls = i === target && typed > 0 ? "line drafted" : "line"
      return `<span class="${cls}"><span class="no">${i + 1}</span>${highlightPython(text)}${caret}</span>`
    }).join("")
    state.textContent = done ? "drafted by our CodeT5 · no API call" : "CodeT5 drafting…"
    state.classList.toggle("done", done)
  }

  clearInterval(pre._timer)
  const full = (lines[target] || "").length
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches
  // Plays once per page load; reruns of the landing page show the finished code.
  if (reduced || window.__codedocaiHeroPlayed) { draw(full, true); return }
  window.__codedocaiHeroPlayed = true
  const indent = (lines[target] || "").search(/\\S/)
  let typed = indent
  draw(typed, false)
  // The window fades in once the headline has typed out (CSS, about 1.6 s);
  // typing starts half a second after that, timed from the hero's start.
  const start = window.__codedocaiHeroStart || (window.__codedocaiHeroStart = performance.now())
  setTimeout(() => {
    pre._timer = setInterval(() => {
      typed += 1
      draw(typed, typed >= full)
      if (typed >= full) clearInterval(pre._timer)
    }, 26)
  }, Math.max(0, 2100 - (performance.now() - start)))
}
"""

_WINDOW = st.components.v2.component("codedocai_code_window", html=_HTML, css=_CSS, js=_JS)


def render() -> None:
    _WINDOW(key="hero_code_window", data={"lines": SAMPLE, "docstring_line": DOCSTRING_LINE}, width="stretch")
