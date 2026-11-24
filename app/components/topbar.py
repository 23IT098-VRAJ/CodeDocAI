"""
The sticky, frosted top bar: wordmark, the five workflow steps, and the account
controls. Clicks come back to Python as a one-run "nav" trigger, handled in a
callback before the screen renders, so a click never costs an extra rerun.
"""

from collections.abc import Callable

import streamlit as st

WORKFLOW_STEPS = [
    ("scan", "Scan"),
    ("generation", "Generate"),
    ("docs", "Docs"),
    ("qa", "Q&A"),
    ("export", "Export"),
]

_HTML = """
<nav class="bar" aria-label="Main">
  <button type="button" class="brand" data-target="landing">CodeDocAI</button>
  <ol class="steps" aria-label="Workflow"></ol>
  <div class="spacer"></div>
  <div class="right"></div>
</nav>
"""

_CSS = """
:host { display: block; }
.bar {
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 56px;
  font-family: var(--font-sans, var(--st-font));
  color: var(--text-primary, var(--st-text-color));
}
button {
  font: inherit;
  color: inherit;
  background: none;
  border: 1px solid transparent;
  border-radius: var(--radius-base, 8px);
  cursor: pointer;
  transition: background-color 150ms ease, border-color 150ms ease, color 150ms ease, scale 150ms ease-out;
}
button:focus-visible { outline: 2px solid var(--accent-amber, #E8B339); outline-offset: 2px; }
@media (prefers-reduced-motion: no-preference) {
  button:not(:disabled):active { scale: 0.96; }
}
.brand {
  font-family: var(--font-serif, var(--st-heading-font));
  font-weight: 700;
  font-size: 1.25rem;
  letter-spacing: -0.02em;
  color: var(--text-primary, #F0EAD9);
  padding: 4px 12px 4px 0;
}
.steps {
  list-style: none;
  display: flex;
  align-items: center;
  gap: 2px;
  margin: 0;
  padding: 0 0 0 12px;
  border-left: 1px solid var(--border, #222222);
}
.steps[hidden] { display: none; }
.steps li { display: flex; align-items: center; }
.steps li + li::before {
  content: "";
  width: 12px;
  height: 1px;
  margin: 0 4px;
  background: var(--border-strong, #5E5E5E);
}
.step {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  min-width: 84px;
  padding: 6px 10px;
  font-size: 0.875rem;
  white-space: nowrap;
  color: var(--text-muted, #A59C8A);
}
.step .mark {
  width: 16px; height: 16px;
  display: inline-flex; align-items: center; justify-content: center;
  border-radius: 999px;
  font-size: 0.6875rem;
  line-height: 1;
}
.step.done .mark { background: var(--accent-amber, #E8B339); color: var(--text-on-accent, #151515); }
.step.done { color: var(--text-primary, #F0EAD9); }
.step.current {
  color: var(--text-on-accent, #151515);
  background: var(--accent-amber, #E8B339);
  border-color: var(--accent-amber, #E8B339);
  font-weight: 500;
  border-radius: 999px;
}
.step.current .mark { background: var(--text-on-accent, #151515); color: var(--accent-amber, #E8B339); }
.step:disabled { opacity: 0.45; cursor: default; }
.spacer { flex: 1; }
.right { display: flex; align-items: center; gap: 8px; }
.badge {
  display: inline-flex; align-items: center; gap: 6px;
  font-size: 0.75rem;
  color: var(--accent-amber, #E8B339);
  background: rgba(232, 179, 57, 0.12);
  border-radius: 999px;
  padding: 4px 10px;
}
.badge::before { content: ""; width: 6px; height: 6px; border-radius: 999px; background: currentColor; }
.model {
  display: inline-flex; align-items: center; gap: 6px;
  font-size: 0.75rem;
  color: var(--text-muted, #A59C8A);
  padding: 4px 6px;
}
.model::before { content: ""; width: 6px; height: 6px; border-radius: 999px; background: var(--color-success, #4CAF50); }
.model.cloud::before { background: var(--accent-amber, #E8B339); }
@media (max-width: 1100px) { .model { display: none; } }
.kbd {
  font-family: var(--font-mono, var(--st-code-font));
  font-size: 0.75rem;
  color: var(--text-muted, #A59C8A);
  border-color: var(--border, #222222);
  padding: 4px 8px;
}
.link { font-size: 0.875rem; color: var(--text-muted, #A59C8A); padding: 6px 10px; }
.user { font-size: 0.875rem; color: var(--text-muted, #A59C8A); padding: 0 4px; }
.outline {
  font-size: 0.875rem;
  padding: 8px 14px;
  border-color: var(--border-strong, #5E5E5E);
  color: var(--text-primary, #F0EAD9);
}
@media (hover: hover) {
  .brand:hover { color: var(--accent-amber, #E8B339); }
  .step:not(:disabled):not(.current):hover, .link:hover, .kbd:hover {
    color: var(--text-primary, #F0EAD9);
    background: var(--surface-raised, #111111);
  }
  .outline:hover { border-color: var(--accent-amber, #E8B339); color: var(--accent-amber, #E8B339); }
}
@media (max-width: 860px) {
  .step { min-width: 0; padding: 6px 8px; }
  .kbd, .link { display: none; }
}
"""

_JS = """
export default function (component) {
  const { data, parentElement, setTriggerValue } = component
  const root = parentElement.querySelector(".bar")
  if (!root) return
  const go = (target) => setTriggerValue("nav", target)

  const make = (tag, cls, text) => {
    const el = document.createElement(tag)
    if (cls) el.className = cls
    if (text !== undefined) el.textContent = text
    return el
  }

  root.querySelector(".brand").onclick = () => go("landing")

  const steps = root.querySelector(".steps")
  steps.replaceChildren()
  steps.hidden = !(data.steps && data.steps.length)
  for (const [index, step] of (data.steps || []).entries()) {
    const li = make("li")
    const button = make("button", "step " + step.state)
    button.type = "button"
    const mark = make("span", "mark", step.state === "done" ? "✓" : String(index + 1))
    mark.setAttribute("aria-hidden", "true")
    button.append(mark, make("span", "", step.label))
    if (step.state === "locked") {
      button.disabled = true
      button.title = "Available after the previous step"
    }
    if (step.state === "current") button.setAttribute("aria-current", "step")
    button.onclick = () => { if (step.state !== "current") go(step.target) }
    li.append(button)
    steps.append(li)
  }

  const right = root.querySelector(".right")
  right.replaceChildren()
  if (data.model) {
    const model = make("span", "model " + data.model, data.model === "local" ? "CodeT5 ready" : "Cloud drafting")
      model.title = data.model === "local"
        ? "CodeDocAI's own CodeT5 model is loaded; docstrings are drafted without any API call."
        : "CodeDocAI's own model didn't load; docstrings are drafted by the cloud fallback."
    right.append(model)
  }
  if (data.offline) {
    const badge = make("span", "badge", "Offline")
    badge.title = "Test mode: cloud answers are placeholders and nothing calls an API."
    right.append(badge)
  }
  const isMac = /Mac|iPhone|iPad/.test(navigator.platform || navigator.userAgent)
  const kbd = make("button", "kbd", isMac ? "⌘K" : "Ctrl K")
  kbd.type = "button"
  kbd.title = "Search screens and functions"
  kbd.setAttribute("aria-label", "Open the command palette")
  kbd.onclick = () => window.dispatchEvent(new CustomEvent("codedocai:palette"))
  right.append(kbd)
  if (data.show_how) {
    const how = make("button", "link", "How it works")
    how.type = "button"
    // On the home page the pipeline is already there: scroll to it. Elsewhere, go home first.
    how.onclick = () => {
      const target = document.getElementById("how-it-works")
      if (!target) return go("how")
      const still = window.matchMedia("(prefers-reduced-motion: reduce)").matches
      target.scrollIntoView({ behavior: still ? "auto" : "smooth", block: "start" })
    }
    right.append(how)
  }
  if (data.user) {
    right.append(make("span", "user", data.user))
    if (data.manager) {
      const log = make("button", "link", "Audit log")
      log.type = "button"
      log.onclick = () => go("manager_dashboard")
      right.append(log)
    }
    const out = make("button", "outline", "Sign out")
    out.type = "button"
    out.onclick = () => go("sign_out")
    right.append(out)
  } else if (data.show_sign_in) {
    const signIn = make("button", "outline", "Sign in")
    signIn.type = "button"
    signIn.onclick = () => go("login")
    right.append(signIn)
  }
}
"""

_TOPBAR = st.components.v2.component("codedocai_topbar", html=_HTML, css=_CSS, js=_JS)

SCREENS = {"landing", "scan", "generation", "docs", "qa", "export", "manager_dashboard"}


def navigate(target: str) -> None:
    """Applies a navigation target from the top bar or the command palette to session state."""
    state = st.session_state
    if target == "sign_out":
        state["authenticated"] = False
        state["role"] = None
        state["username"] = None
        state["current_screen"] = "landing"
    elif target == "login":
        # Remember where the visitor was, so signing in (or backing out) returns them there.
        state["_return_screen"] = state.get("current_screen", "landing")
        state["current_screen"] = "login"
    elif target == "how":
        # How it works is a section of the home page; app.py scrolls to it after the switch.
        state["current_screen"] = "landing"
        state["_scroll_anchor"] = "how-it-works"
    elif target in SCREENS:
        state["current_screen"] = target


def _trigger(key: str, name: str):
    value = st.session_state.get(key)
    return getattr(value, name, None) if not isinstance(value, dict) else value.get(name)


def _on_nav() -> None:
    target = _trigger("topbar", "nav")
    if target:
        navigate(target)


def step_states(current_screen: str) -> list[dict]:
    """Each workflow step as done, current, available or locked."""
    populated = st.session_state.get("scan_status") == "populated"
    generated = bool(st.session_state.get("generation_complete"))
    reachable = {"scan": True, "generation": populated, "docs": generated, "qa": generated, "export": generated}
    done = {"scan": populated, "generation": generated}
    steps = []
    for target, label in WORKFLOW_STEPS:
        if target == current_screen:
            state = "current"
        elif not reachable[target]:
            state = "locked"
        elif done.get(target):
            state = "done"
        else:
            state = "available"
        steps.append({"target": target, "label": label, "state": state})
    return steps


def render(current_screen: str, offline: str | None = None, on_nav: Callable[[], None] | None = None) -> None:
    """Mounts the top bar. The caller's container makes it sticky."""
    in_workflow = current_screen in dict(WORKFLOW_STEPS)
    data = {
        "steps": step_states(current_screen) if in_workflow else [],
        "offline": bool(offline),
        "model": ("local" if st.session_state.get("ai_engine") else "cloud") if "ai_engine" in st.session_state else None,
        "show_how": not in_workflow,
        "user": st.session_state.get("username") if st.session_state.get("authenticated") else None,
        "manager": st.session_state.get("authenticated") and st.session_state.get("role") == "manager"
                   and current_screen != "manager_dashboard",
        "show_sign_in": current_screen != "login",
    }
    _TOPBAR(key="topbar", data=data, on_nav_change=on_nav or _on_nav, width="stretch")
