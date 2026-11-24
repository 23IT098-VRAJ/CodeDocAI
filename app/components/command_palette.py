"""
The ⌘K / Ctrl+K command palette: a fuzzy search over screens, actions and every
parsed function. It opens from the keyboard shortcut or the top bar's hint
badge (a window event), and returns the chosen command as a one-run trigger.
"""

import streamlit as st

_HTML = """
<div class="overlay" hidden>
  <div class="panel" role="dialog" aria-modal="true" aria-label="Command palette">
    <input class="search" type="text" placeholder="Jump to a screen or function…"
           aria-label="Search commands" autocomplete="off" spellcheck="false" />
    <ul class="results" role="listbox" aria-label="Commands"></ul>
    <div class="footer"><span>↑↓ to move</span><span>Enter to open</span><span>Esc to close</span></div>
  </div>
</div>
"""

_CSS = """
:host { display: block; height: 0; }
.overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding-top: 12vh;
  background: rgba(0, 0, 0, 0.6);
  font-family: var(--font-mono, var(--st-font));
}
.overlay[hidden] { display: none; }
@media (prefers-reduced-motion: no-preference) {
  .overlay:not([hidden]) .panel { animation: enter 150ms ease-out; }
}
@keyframes enter { from { opacity: 0; transform: translateY(-6px); } to { opacity: 1; transform: none; } }
.panel {
  width: min(640px, calc(100vw - 32px));
  background: var(--surface, #0A0A0A);
  border: 1px solid var(--border-strong, #5E5E5E);
  border-radius: var(--radius-md, 12px);
  overflow: hidden;
  color: var(--text-primary, #F0EAD9);
}
.search {
  width: 100%;
  box-sizing: border-box;
  font: inherit;
  font-size: 1rem;
  color: inherit;
  background: transparent;
  border: none;
  border-bottom: 1px solid var(--border, #222222);
  padding: 16px 18px;
  outline: none;
}
.search::placeholder { color: var(--text-placeholder, #A0A0A0); }
.results { list-style: none; margin: 0; padding: 6px; max-height: 48vh; overflow-y: auto; overscroll-behavior: contain; }
.results li {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 9px 12px;
  border-radius: var(--radius-base, 8px);
  cursor: pointer;
  font-size: 0.875rem;
}
.results li[aria-selected="true"] { background: var(--surface-raised, #111111); box-shadow: inset 2px 0 0 var(--accent-amber, #E8B339); }
.results .group {
  font-size: 0.6875rem;
  color: var(--text-muted, #A59C8A);
  min-width: 68px;
}
.results .label { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.results .hint { font-size: 0.75rem; color: var(--text-muted, #A59C8A); }
.results mark { background: none; color: var(--accent-amber, #E8B339); }
.results .empty { color: var(--text-muted, #A59C8A); cursor: default; }
.footer {
  display: flex;
  gap: 16px;
  padding: 8px 18px;
  border-top: 1px solid var(--border, #222222);
  font-size: 0.6875rem;
  color: var(--text-muted, #A59C8A);
}
"""

_JS = """
function score(query, text) {
  // Subsequence match: every query character in order. Earlier, tighter matches score higher.
  if (!query) return { score: 1, hits: [] }
  const q = query.toLowerCase(), t = text.toLowerCase()
  let ti = 0, s = 0, last = -1
  const hits = []
  for (const ch of q) {
    const found = t.indexOf(ch, ti)
    if (found < 0) return null
    s += found === last + 1 ? 3 : 1
    if (found === 0 || /[\\s_./]/.test(t[found - 1])) s += 2
    hits.push(found)
    last = found
    ti = found + 1
  }
  return { score: s - t.length * 0.01, hits }
}

function mark(text, hits) {
  const set = new Set(hits)
  let out = ""
  for (const [i, ch] of [...text].entries()) {
    const safe = ch.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    out += set.has(i) ? `<mark>${safe}</mark>` : safe
  }
  return out
}

export default function (component) {
  const { data, parentElement, setTriggerValue } = component
  const overlay = parentElement.querySelector(".overlay")
  const input = parentElement.querySelector(".search")
  const list = parentElement.querySelector(".results")
  if (!overlay || !input || !list) return
  const commands = data.commands || []
  let shown = [], active = 0

  const render = () => {
    const query = input.value.trim()
    shown = commands
      .map((c) => ({ c, m: score(query, c.label) }))
      .filter((x) => x.m)
      .sort((a, b) => b.m.score - a.m.score)
      .slice(0, 50)
    active = Math.min(active, Math.max(shown.length - 1, 0))
    list.replaceChildren()
    if (!shown.length) {
      const li = document.createElement("li")
      li.className = "empty"
      li.textContent = "No matches"
      list.append(li)
      return
    }
    shown.forEach(({ c, m }, i) => {
      const li = document.createElement("li")
      li.setAttribute("role", "option")
      li.setAttribute("aria-selected", String(i === active))
      li.innerHTML = `<span class="group"></span><span class="label">${mark(c.label, m.hits)}</span><span class="hint"></span>`
      li.querySelector(".group").textContent = c.group
      li.querySelector(".hint").textContent = c.hint || ""
      li.onmouseenter = () => { active = i; paint() }
      li.onclick = () => choose(i)
      list.append(li)
    })
  }
  const paint = () => {
    [...list.children].forEach((li, i) => li.setAttribute("aria-selected", String(i === active)))
    list.children[active]?.scrollIntoView({ block: "nearest" })
  }
  const open = () => {
    overlay.hidden = false
    input.value = ""
    active = 0
    render()
    input.focus()
  }
  const close = () => { overlay.hidden = true }
  const choose = (i) => {
    const item = shown[i]
    if (!item) return
    close()
    setTriggerValue("command", item.c.id)
  }

  input.oninput = () => { active = 0; render() }
  input.onkeydown = (e) => {
    if (e.key === "ArrowDown") { active = Math.min(active + 1, shown.length - 1); paint(); e.preventDefault() }
    else if (e.key === "ArrowUp") { active = Math.max(active - 1, 0); paint(); e.preventDefault() }
    else if (e.key === "Enter") { choose(active); e.preventDefault() }
    else if (e.key === "Escape") { close(); e.preventDefault() }
  }
  overlay.onclick = (e) => { if (e.target === overlay) close() }

  // One global listener per page: this function runs again on every rerun, so the
  // previous handlers are replaced instead of stacking up.
  if (window.__codedocaiPalette) {
    window.removeEventListener("keydown", window.__codedocaiPalette.key)
    window.removeEventListener("codedocai:palette", window.__codedocaiPalette.open)
  }
  const onKey = (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") { e.preventDefault(); overlay.hidden ? open() : close() }
  }
  window.__codedocaiPalette = { key: onKey, open }
  window.addEventListener("keydown", onKey)
  window.addEventListener("codedocai:palette", open)
}
"""

_PALETTE = st.components.v2.component("codedocai_command_palette", html=_HTML, css=_CSS, js=_JS)

MAX_FUNCTIONS = 400


def build_commands(current_screen: str) -> list[dict]:
    """Every command the palette offers right now: reachable screens, actions and parsed functions."""
    populated = st.session_state.get("scan_status") == "populated"
    generated = bool(st.session_state.get("generation_complete"))
    screens = [
        ("landing", "Home", True),
        ("architecture", "How it works", True),
        ("scan", "Scan", True),
        ("generation", "Generate", populated),
        ("docs", "Documentation", generated),
        ("qa", "Ask the codebase", generated),
        ("export", "Export", generated),
    ]
    if st.session_state.get("authenticated") and st.session_state.get("role") == "manager":
        screens.append(("manager_dashboard", "Audit log", True))
    commands = [
        {"id": f"screen:{target}", "label": label, "group": "Go to", "hint": "current" if target == current_screen else ""}
        for target, label, available in screens if available
    ]
    if populated or generated:
        commands.append({"id": "action:new_scan", "label": "Start a new scan", "group": "Action", "hint": "asks first"})
    if not st.session_state.get("authenticated"):
        commands.append({"id": "action:sign_in", "label": "Sign in", "group": "Action", "hint": ""})
    for fn in ((st.session_state.get("pipeline_results") or {}).get("functions") or [])[:MAX_FUNCTIONS]:
        name = fn.get("name", "")
        commands.append({"id": f"function:{name}", "label": name, "group": "Function", "hint": fn.get("file", "")})
    return commands


def _on_command() -> None:
    from components.topbar import navigate

    value = st.session_state.get("command_palette")
    command = value.get("command") if isinstance(value, dict) else getattr(value, "command", None)
    if not command:
        return
    kind, _, arg = command.partition(":")
    state = st.session_state
    if kind == "screen":
        navigate(arg)
    elif kind == "function":
        # Docs opens filtered to that function; the filter widgets read these keys on render.
        state["docs_filter"] = arg
        state["docs_filter_show"] = "All"
        navigate("docs")
    elif command == "action:sign_in":
        navigate("login")
    elif command == "action:new_scan":
        has_work = bool(state.get("generation_complete") or state.get("pipeline_results") or state.get("qa_chat_history"))
        state["current_screen"] = "scan"
        if has_work:
            state["_confirm_new_scan"] = "cta_scan_reset"  # the scan screen's New scan dialog opens


def render(current_screen: str) -> None:
    _PALETTE(key="command_palette", data={"commands": build_commands(current_screen)},
             on_command_change=_on_command, width="stretch")
