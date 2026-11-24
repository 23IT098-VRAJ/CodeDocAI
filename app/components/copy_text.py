"""
Click-to-copy text: a docstring with a small Copy button, or a row of citation
pills that each copy their own text. Shows "Copied" on success.
"""

import streamlit as st

_HTML = """
<div class="root"></div>
"""

_CSS = """
:host { display: block; }
.root { font-family: var(--font-sans, var(--st-font)); }
.doc {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}
.doc p {
  margin: 0;
  flex: 1;
  font-size: 1rem;
  line-height: 1.5;
  color: var(--text-primary, #F0EAD9);
}
.copy, .pill {
  font: inherit;
  cursor: pointer;
  transition: border-color 150ms ease, color 150ms ease, background-color 150ms ease, scale 150ms ease-out;
}
.copy {
  flex: none;
  font-size: 0.75rem;
  color: var(--text-muted, #A59C8A);
  background: transparent;
  border: 1px solid var(--border, #222222);
  border-radius: var(--radius-sm, 4px);
  padding: 2px 8px;
}
.pills { display: flex; flex-wrap: wrap; gap: 6px; }
.pill {
  font-family: var(--font-mono, var(--st-code-font));
  font-size: 0.75rem;
  color: var(--accent-amber, #E8B339);
  background: rgba(232, 179, 57, 0.05);
  border: 1px solid var(--border-strong, #5E5E5E);
  border-radius: 999px;
  padding: 2px 10px;
}
.copy.done, .pill.done { color: var(--color-success, #4CAF50); border-color: var(--color-success, #4CAF50); }
.copy:focus-visible, .pill:focus-visible { outline: 2px solid var(--accent-amber, #E8B339); outline-offset: 2px; }
@media (hover: hover) {
  .copy:hover { color: var(--text-primary, #F0EAD9); border-color: var(--border-strong, #5E5E5E); }
  .pill:hover { border-color: var(--accent-amber, #E8B339); }
}
@media (prefers-reduced-motion: no-preference) {
  .copy:active, .pill:active { scale: 0.96; }
}
"""

_JS = """
async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text)
    return true
  } catch (error) {
    const area = document.createElement("textarea")
    area.value = text
    area.setAttribute("readonly", "")
    area.style.position = "fixed"
    area.style.opacity = "0"
    document.body.append(area)
    area.select()
    let ok = false
    try { ok = document.execCommand("copy") } catch (e) { ok = false }
    area.remove()
    return ok
  }
}

function wire(button, text, idle) {
  button.onclick = async () => {
    const ok = await copyText(text)
    button.textContent = ok ? "Copied" : "Copy failed"
    button.classList.toggle("done", ok)
    clearTimeout(button._timer)
    button._timer = setTimeout(() => { button.textContent = idle; button.classList.remove("done") }, 1400)
  }
}

export default function (component) {
  const { data, parentElement } = component
  const root = parentElement.querySelector(".root")
  if (!root) return
  root.replaceChildren()
  if (data.variant === "pills") {
    const row = document.createElement("div")
    row.className = "pills"
    row.setAttribute("aria-label", "Sources")
    for (const item of data.items || []) {
      const pill = document.createElement("button")
      pill.type = "button"
      pill.className = "pill"
      pill.textContent = item
      pill.title = "Copy " + item
      wire(pill, item, item)
      row.append(pill)
    }
    root.append(row)
    return
  }
  const doc = document.createElement("div")
  doc.className = "doc"
  const text = document.createElement("p")
  text.textContent = data.text || ""
  const button = document.createElement("button")
  button.type = "button"
  button.className = "copy"
  button.textContent = "Copy"
  button.setAttribute("aria-label", "Copy docstring")
  wire(button, data.text || "", "Copy")
  doc.append(text, button)
  root.append(doc)
}
"""

_COPY = st.components.v2.component("codedocai_copy_text", html=_HTML, css=_CSS, js=_JS)


def docstring(text: str, *, key: str) -> None:
    """A docstring with a Copy button beside it."""
    _COPY(key=key, data={"variant": "docstring", "text": text}, width="stretch")


def pills(items: list[str], *, key: str) -> None:
    """Citation pills; clicking one copies it (for example `spider.py::crawl_page()`)."""
    if items:
        _COPY(key=key, data={"variant": "pills", "items": items}, width="stretch")
