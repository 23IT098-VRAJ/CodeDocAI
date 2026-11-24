"""
The home page's How it works: a stepper on the left (four numbered steps on a
rail) and a stage on the right where each step plays a small animated picture.

It loops on its own once it scrolls into view. The rail segment under the
active step fills while that step plays; when it is full the next step starts.
The Pause button (WCAG 2.2.2 asks for one on anything that moves for more
than five seconds) or scrolling it off screen pause the rail and the stage's
animations together: one class on the root pauses every animation inside it.
Each stage's picture is timed to keep moving for most of its step. Clicking a
step jumps to it and the loop carries on from there. Arrow keys move between steps. Under
prefers-reduced-motion nothing plays on its own and nothing moves.

The file names, function names and drafts come from the Spider sample run.
"""

import streamlit as st

from components._syntax import HIGHLIGHT_JS, SYNTAX_CSS

STAGE_MS = 8000

_HTML = """
<div class="tour">
  <div class="steps" role="tablist" aria-orientation="vertical" aria-label="How it works"></div>
  <div class="stage">
    <p class="stage-desc"></p>
    <div class="panel" role="tabpanel" tabindex="0"></div>
    <button class="pp" type="button" hidden></button>
  </div>
</div>
"""

_CSS = """
:host { display: block; }
.tour {
  font-family: var(--font-sans, "Inter", sans-serif);
  color: var(--text-primary, #F0EAD9);
  display: grid;
  grid-template-columns: minmax(15rem, 20rem) minmax(0, 1fr);
  gap: 40px;
  align-items: stretch;
}

/* ---- Stepper: numbered nodes on a rail ---- */
.steps { display: flex; flex-direction: column; padding-top: 6px; }
.step {
  position: relative;
  appearance: none;
  border: 0;
  background: transparent;
  color: inherit;
  font: inherit;
  text-align: left;
  cursor: pointer;
  display: grid;
  grid-template-columns: 36px minmax(0, 1fr);
  column-gap: 16px;
  padding: 0 0 26px;
  border-radius: 12px;
}
.step:last-child { padding-bottom: 6px; }
.node {
  position: relative;
  z-index: 1;
  width: 36px;
  height: 36px;
  border-radius: 999px;
  display: grid;
  place-items: center;
  font-family: var(--font-mono, monospace);
  font-size: 0.8125rem;
  color: var(--text-muted, #A59C8A);
  background: var(--bg, #000000);
  border: 1px solid var(--border-strong, #5E5E5E);
  transition: background-color 200ms ease, color 200ms ease, border-color 200ms ease, box-shadow 200ms ease, transform 200ms ease;
}
.rail {
  position: absolute;
  left: 17px;
  top: 40px;
  bottom: 4px;
  width: 2px;
  border-radius: 999px;
  background: var(--border, #222222);
  overflow: hidden;
}
.step:last-child .rail { display: none; }
.rail i { display: block; width: 100%; height: 100%; background: var(--accent-amber, #E8B339); transform-origin: top; transform: scaleY(0); }
.done .rail i { transform: scaleY(1); }
.text { display: flex; flex-direction: column; gap: 3px; padding-top: 6px; min-width: 0; }
.name { font-size: 1.0625rem; font-weight: 600; color: var(--text-muted, #A59C8A); transition: color 200ms ease; }
.fig { font-family: var(--font-mono, monospace); font-size: 0.75rem; color: var(--text-muted, #A59C8A); }
.desc {
  font-size: 0.875rem;
  line-height: 1.5;
  color: var(--text-muted, #A59C8A);
  display: grid;
  grid-template-rows: 0fr;
  opacity: 0;
  transition: grid-template-rows 300ms cubic-bezier(0.2, 0, 0, 1), opacity 300ms ease, margin-top 300ms ease;
}
.desc > span { overflow: hidden; }
.step[aria-selected="true"] .desc { grid-template-rows: 1fr; opacity: 1; margin-top: 6px; }
.step[aria-selected="true"] .name { color: var(--text-strong, #FFFFFF); }
.step[aria-selected="true"] .fig { color: var(--accent-amber, #E8B339); }
.step[aria-selected="true"] .node {
  color: var(--text-on-accent, #1A1A1A);
  background: var(--accent-amber, #E8B339);
  border-color: var(--accent-amber, #E8B339);
  box-shadow: 0 0 0 6px var(--accent-glow, rgba(232, 179, 57, 0.14));
}
.done .node { color: var(--accent-amber, #E8B339); border-color: var(--accent-amber, #E8B339); }
@media (hover: hover) {
  .step:hover .name { color: var(--text-primary, #F0EAD9); }
  .step:not([aria-selected="true"]):hover .node { border-color: var(--accent-amber, #E8B339); color: var(--accent-amber, #E8B339); transform: scale(1.08); }
}
.step:focus-visible { outline: 2px solid var(--accent-amber, #E8B339); outline-offset: 4px; }

/* the active step's rail fills while it plays; the next step starts when it is full */
.playing .step[aria-selected="true"] .rail i { animation: fill var(--stage-ms) linear both; }
.playing .step:last-child[aria-selected="true"] .node::after {
  content: "";
  position: absolute;
  inset: -4px;
  border-radius: 999px;
  border: 2px solid var(--accent-amber, #E8B339);
  animation: ring var(--stage-ms) linear both;
}
@keyframes fill { from { transform: scaleY(0); } to { transform: scaleY(1); } }
@keyframes ring { from { clip-path: inset(0 0 100% 0); } to { clip-path: inset(0 0 0 0); } }

/* ---- Stage: an open canvas, not a box ---- */
.stage {
  position: relative;
  border-radius: 20px;
  border: 1px solid var(--border-faint, rgba(255, 255, 255, 0.05));
  background:
    radial-gradient(rgba(255, 255, 255, 0.06) 1px, transparent 1px) 0 0 / 18px 18px,
    var(--surface, #0A0A0A);
  padding: 32px;
  min-height: 360px;
  display: grid;
  align-items: center;
}
.stage-desc { display: none; }
.panel { outline: none; }
.panel:focus-visible { outline: 2px solid var(--accent-amber, #E8B339); outline-offset: 8px; border-radius: 8px; }
.pp {
  position: absolute;
  right: 14px;
  bottom: 14px;
  appearance: none;
  font: inherit;
  font-family: var(--font-mono, monospace);
  font-size: 0.75rem;
  color: var(--text-muted, #A59C8A);
  background: var(--bg, #000000);
  border: 1px solid var(--border-strong, #5E5E5E);
  border-radius: 999px;
  padding: 5px 12px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}
.pp::before { content: ""; width: 8px; height: 10px; border-left: 3px solid currentColor; border-right: 3px solid currentColor; box-sizing: border-box; }
.pp.is-held::before { width: 0; height: 0; border-style: solid; border-width: 5px 0 5px 9px; border-color: transparent transparent transparent currentColor; }
.pp:focus-visible { outline: 2px solid var(--accent-amber, #E8B339); outline-offset: 2px; }
@media (hover: hover) { .pp:hover { color: var(--accent-amber, #E8B339); border-color: var(--accent-amber, #E8B339); } }

/* Paused (the button, or off screen): every animation inside stops where it is. */
.tour.paused *, .tour.paused *::before, .tour.paused *::after { animation-play-state: paused !important; }

.mono { font-family: var(--font-mono, monospace); }

/* ---- Stage pictures. Each one is timed to keep moving for most of its step
   (STAGE_MS); delays are absolute milliseconds from the moment the step starts. ---- */

/* Scan: a beam walks down the files; each file lights up, its functions pop in */
.scan { display: flex; flex-direction: column; gap: 18px; }
.files { position: relative; display: flex; flex-direction: column; gap: 10px; }
.beam { position: absolute; left: -14px; right: -14px; height: 34px; top: 0; pointer-events: none; opacity: 0;
  background: linear-gradient(180deg, transparent, rgba(232, 179, 57, 0.12));
  border-bottom: 1px solid var(--accent-amber, #E8B339); }
.file { display: grid; grid-template-columns: 8.5rem minmax(0, 1fr) auto; gap: 12px; align-items: start; }
.file .path { font-family: var(--font-mono, monospace); font-size: 0.8125rem; color: var(--text-primary, #F0EAD9); padding-top: 3px; }
.file .cnt { font-family: var(--font-mono, monospace); font-size: 0.75rem; color: var(--accent-amber, #E8B339); padding-top: 4px; white-space: nowrap; }
.chips { display: flex; flex-wrap: wrap; gap: 6px; }
.chip {
  font-family: var(--font-mono, monospace);
  font-size: 0.75rem;
  padding: 3px 9px;
  border-radius: 999px;
  border: 1px solid var(--border-strong, #5E5E5E);
  background: var(--bg, #000000);
  color: var(--text-muted, #A59C8A);
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.chip::before { content: ""; width: 6px; height: 6px; border-radius: 999px; background: var(--accent-amber, #E8B339); }
.scan-foot { display: flex; flex-wrap: wrap; align-items: baseline; gap: 28px; padding-top: 14px; border-top: 1px solid var(--border, #222222);
  font-family: var(--font-mono, monospace); font-size: 0.8125rem; color: var(--text-muted, #A59C8A); }
.scan-foot b { color: var(--accent-amber, #E8B339); font-weight: 500; font-size: 1.375rem; margin-right: 6px; }
.ok { margin-left: auto; color: var(--color-success, #4CAF50); }

/* Draft: each docstring line opens, types out, then the next function */
.draft { display: flex; flex-direction: column; gap: 18px; }
.code { margin: 0; font-family: var(--font-mono, monospace); font-size: 0.8125rem; line-height: 1.75; white-space: pre; overflow-x: auto; }
.code .doc { color: var(--color-success, #4CAF50); display: inline-block; overflow: hidden; vertical-align: bottom; white-space: pre; }
.code .row-doc { display: block; overflow: hidden; background: rgba(76, 175, 80, 0.08); box-shadow: inset 2px 0 0 var(--color-success, #4CAF50); }
.code .gap { display: block; height: 0.7em; }
.status { display: grid; font-family: var(--font-mono, monospace); font-size: 0.75rem; color: var(--text-muted, #A59C8A);
  padding-top: 14px; border-top: 1px solid var(--border, #222222); }
.status > span { grid-area: 1 / 1; }
.status b { color: var(--accent-amber, #E8B339); font-weight: 500; }
.status .end { color: var(--color-success, #4CAF50); }

/* Map: outline lines go out as packets; the overview fills section by section */
.flow { display: grid; grid-template-columns: minmax(0, 1fr) 9rem minmax(0, 1fr); gap: 16px; align-items: center; }
.outline { display: flex; flex-direction: column; gap: 6px; font-family: var(--font-mono, monospace); font-size: 0.75rem; color: var(--text-muted, #A59C8A); }
.outline b { color: var(--text-primary, #F0EAD9); font-weight: 500; }
.wire { display: flex; flex-direction: column; align-items: center; gap: 10px; font-family: var(--font-mono, monospace); font-size: 0.75rem; color: var(--accent-amber, #E8B339); text-align: center; }
.wire .line { position: relative; width: 100%; height: 2px; background: var(--border, #222222); border-radius: 999px; }
.wire .pkt { position: absolute; top: -3px; left: 0; width: 8px; height: 8px; border-radius: 999px; background: var(--accent-amber, #E8B339); box-shadow: 0 0 10px var(--accent-amber, #E8B339); opacity: 0; }
.doc-card { position: relative; border: 1px solid var(--border, #222222); border-radius: 12px; padding: 16px; background: var(--surface-sunken, #050505); }
.doc-card .title { font-family: var(--font-mono, monospace); font-size: 0.75rem; color: var(--accent-amber, #E8B339); margin-bottom: 12px; }
.doc-card .h { font-size: 0.8125rem; font-weight: 600; margin: 10px 0 6px; }
.doc-card .ln { height: 6px; border-radius: 999px; background: var(--border-strong, #5E5E5E); margin-bottom: 6px; transform-origin: left; }
.doc-card .stamp { position: absolute; top: 14px; right: 14px; font-family: var(--font-mono, monospace); font-size: 0.75rem; color: var(--color-success, #4CAF50); }

/* Ask: the question arrives, the index is searched, the answer streams in */
.ask { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.4fr); gap: 24px; align-items: start; }
.q { font-weight: 600; font-size: 1rem; margin: 0 0 14px; }
.who { display: block; font-family: var(--font-mono, monospace); font-size: 0.75rem; color: var(--text-muted, #A59C8A); margin-bottom: 4px; font-weight: 400; }
.passages { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 6px; }
.passages li { font-family: var(--font-mono, monospace); font-size: 0.75rem; padding: 6px 10px; border-radius: 8px; border: 1px solid var(--accent-edge, rgba(232, 179, 57, 0.45)); background: var(--bg, #000000); color: var(--text-primary, #F0EAD9); }
.passages li span { color: var(--accent-amber, #E8B339); margin-right: 8px; }
.answer { margin: 0; color: var(--text-primary, #F0EAD9); font-size: 0.9375rem; line-height: 1.6; }
.cites { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 12px; }
.cite { font-family: var(--font-mono, monospace); font-size: 0.75rem; color: var(--accent-amber, #E8B339); border: 1px solid var(--accent-amber, #E8B339); border-radius: 999px; padding: 2px 10px; }
.note { font-family: var(--font-mono, monospace); font-size: 0.75rem; color: var(--text-muted, #A59C8A); margin-top: 10px; }

@media (prefers-reduced-motion: no-preference) {
  /* Scan: 0.2-5.2 s beam, files light as it passes, totals at 5.6 s, ready at 6.3 s */
  .anim .beam { animation: sweep 5000ms linear 200ms both; }
  .anim .file { animation: light 500ms ease-out both; animation-delay: calc(300ms + var(--f) * 1000ms); }
  .anim .chip { animation: pop 300ms cubic-bezier(0.2, 0, 0, 1) both; animation-delay: calc(450ms + var(--f) * 1000ms + var(--i) * 110ms); }
  .anim .file .cnt { animation: pop 300ms cubic-bezier(0.2, 0, 0, 1) both; animation-delay: calc(1000ms + var(--f) * 1000ms); }
  .anim .scan-foot > span { animation: rise 400ms cubic-bezier(0.2, 0, 0, 1) both; animation-delay: calc(5500ms + var(--i) * 150ms); }
  .anim .scan-foot .ok { animation: rise 400ms cubic-bezier(0.2, 0, 0, 1) 6300ms both; }

  /* Draft: each row opens at --d, its docstring types for --t; the status line follows along */
  .anim .code .row-doc { animation: open-row 220ms ease-out both; animation-delay: var(--d); }
  .anim .code .doc { animation: type var(--t) steps(var(--chars), end) both, caret var(--t) steps(1, end) both; animation-delay: calc(var(--d) + 220ms); }
  .anim .status > span { animation: window var(--len) linear both; animation-delay: var(--d); }
  .anim .status > .end { animation: rise 400ms cubic-bezier(0.2, 0, 0, 1) both; animation-delay: var(--d); }

  /* Map: outline 0.2-1.2 s, packets 1.3-6.3 s, overview sections 1.8-6.2 s, stamp 6.5 s */
  .anim .outline div { animation: rise 320ms cubic-bezier(0.2, 0, 0, 1) both; animation-delay: calc(200ms + var(--i) * 220ms); }
  .anim .wire .pkt { animation: travel 1250ms cubic-bezier(0.4, 0, 0.2, 1) 4; animation-delay: calc(1300ms + var(--i) * 410ms); }
  .anim .doc-card { animation: rise 420ms cubic-bezier(0.2, 0, 0, 1) 1500ms both; }
  .anim .doc-card .h { animation: rise 320ms cubic-bezier(0.2, 0, 0, 1) both; animation-delay: calc(1900ms + var(--k) * 1450ms); }
  .anim .doc-card .ln { animation: grow 650ms cubic-bezier(0.2, 0, 0, 1) both; animation-delay: calc(2200ms + var(--i) * 725ms); }
  .anim .doc-card .stamp { animation: pop 300ms cubic-bezier(0.2, 0, 0, 1) 6500ms both; }

  /* Ask: question 0.15-1.0 s, passages 1.4-3.2 s, answer words from 3.4 s, sources 6.0 s */
  .anim .q .w { animation: show 1ms steps(1, start) both; animation-delay: calc(150ms + var(--w) * 90ms); }
  .anim .search { animation: rise 300ms ease-out 1100ms both; }
  .anim .passages li { animation: lit 600ms ease-out both; animation-delay: calc(1400ms + var(--i) * 450ms); }
  .anim .answer-who { animation: rise 300ms ease-out 3200ms both; }
  .anim .answer .w { animation: show 1ms steps(1, start) both; animation-delay: calc(3400ms + var(--w) * 70ms); }
  .anim .cites .cite { animation: pop 300ms cubic-bezier(0.2, 0, 0, 1) both; animation-delay: calc(6000ms + var(--i) * 180ms); }
  .anim .note { animation: rise 400ms ease-out 6500ms both; }
}
@keyframes pop { from { opacity: 0; transform: scale(0.8); } to { opacity: 1; transform: none; } }
@keyframes rise { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }
@keyframes show { from { opacity: 0; } to { opacity: 1; } }
@keyframes sweep { 0% { top: -34px; opacity: 0; } 4% { opacity: 1; } 96% { opacity: 1; } 100% { top: 100%; opacity: 0; } }
@keyframes light { from { opacity: 0.25; } to { opacity: 1; } }
@keyframes open-row { from { max-height: 0; } to { max-height: 2em; } }
@keyframes type { from { width: 0; } to { width: calc(var(--chars) * 1ch); } }
@keyframes caret { from { box-shadow: inset -2px 0 0 var(--accent-amber, #E8B339); } to { box-shadow: none; } }
@keyframes window { 0% { opacity: 0; } 8% { opacity: 1; } 92% { opacity: 1; } 100% { opacity: 0; } }
@keyframes travel { 0% { left: 0; opacity: 0; } 15% { opacity: 1; } 85% { opacity: 1; } 100% { left: calc(100% - 8px); opacity: 0; } }
@keyframes grow { from { transform: scaleX(0); } to { transform: scaleX(1); } }
@keyframes lit {
  from { border-color: var(--border, #222222); color: var(--text-muted, #A59C8A); box-shadow: none; }
  40% { border-color: var(--accent-amber, #E8B339); color: var(--text-primary, #F0EAD9); box-shadow: 0 0 0 3px var(--accent-glow, rgba(232, 179, 57, 0.14)); }
  to { border-color: var(--accent-edge, rgba(232, 179, 57, 0.45)); color: var(--text-primary, #F0EAD9); box-shadow: none; }
}

@media (max-width: 640px) {
  .tour { grid-template-columns: minmax(0, 1fr); gap: 16px; }
  .steps { flex-direction: row; gap: 6px; padding-top: 0; }
  .step { flex: 1; grid-template-columns: minmax(0, 1fr); padding: 0 0 10px; justify-items: center; text-align: center; }
  .text { align-items: center; }
  .fig, .desc { display: none; }
  .rail { left: 0; right: 0; top: auto; bottom: 0; width: auto; height: 2px; }
  .step:last-child .rail { display: block; }
  .rail i { transform-origin: left; transform: scaleX(0); }
  .done .rail i { transform: scaleX(1); }
  .playing .step[aria-selected="true"] .rail i { animation-name: fill-x; }
  .playing .step:last-child[aria-selected="true"] .node::after { display: none; }
  .stage { padding: 18px; min-height: 0; }
  .stage-desc { display: block; margin: 0 0 14px; font-size: 0.875rem; line-height: 1.5; color: var(--text-muted, #A59C8A); }
  .file, .flow, .ask { grid-template-columns: minmax(0, 1fr); }
  .wire .line { width: 60%; }
  .pp { position: static; margin-top: 16px; justify-self: start; }
}
@keyframes fill-x { from { transform: scaleX(0); } to { transform: scaleX(1); } }
""" + SYNTAX_CSS

_JS = HIGHLIGHT_JS + """
const esc = (text) => escapeHtml(String(text))

function renderParse(s) {
  const files = s.files.map((f, fi) =>
    `<div class="file" style="--f:${fi}"><span class="path">${esc(f.path)}</span><span class="chips">` +
    f.functions.map((name, i) => `<span class="chip" style="--i:${i}">${esc(name)}</span>`).join("") +
    `</span><span class="cnt">${f.count} fn</span></div>`).join("")
  const t = s.tally.map(([n, label], i) => `<span style="--i:${i}"><b>${esc(n)}</b>${esc(label)}</span>`).join("")
  return `<div class="scan"><div class="files">${files}<span class="beam"></span></div>` +
    `<div class="scan-foot">${t}<span class="ok">${esc(s.done)}</span></div></div>`
}

function renderDraft(s) {
  // Timeline: each function's docstring row opens, then types at CHAR_MS per character.
  const CHAR_MS = 38, OPEN_MS = 220, GAP_MS = 430
  let at = 400
  const status = []
  const rows = s.functions.map((fn, k) => {
    const chars = fn.doc.length
    const typing = chars * CHAR_MS
    const row = `<span>${highlightPython(fn.def)}</span>\\n` +
      `<span class="row-doc" style="--d:${at}ms">${" ".repeat(fn.indent)}<span class="doc" style="--chars:${chars};--t:${typing}ms;--d:${at}ms">${esc(fn.doc)}</span></span>` +
      fn.body.map((line) => `<span>${highlightPython(line)}</span>`).join("\\n") +
      (k < s.functions.length - 1 ? '<span class="gap"></span>' : "")
    status.push(`<span style="--d:${at}ms;--len:${OPEN_MS + typing + GAP_MS}ms">CodeT5 · drafting <b>${esc(fn.name)}</b> · ${k + 1} of ${s.functions.length}</span>`)
    at += OPEN_MS + typing + GAP_MS
    return row
  }).join("")
  status.push(`<span class="end" style="--d:${at}ms">${esc(s.done)}</span>`)
  return `<div class="draft"><pre class="code">${rows}</pre><div class="status">${status.join("")}</div></div>`
}

function renderOverview(s) {
  const outline = s.outline.map(([file, names], i) => `<div style="--i:${i}"><b>${esc(file)}</b> ${esc(names)}</div>`).join("")
  const widths = [92, 78, 85, 60, 88, 70]
  const pkts = [0, 1, 2].map((i) => `<span class="pkt" style="--i:${i}"></span>`).join("")
  const sections = s.sections.map((h, k) =>
    `<div class="h" style="--k:${k}">${esc(h)}</div>` +
    [0, 1].map((j) => `<div class="ln" style="--i:${k * 2 + j};width:${widths[k * 2 + j]}%"></div>`).join("")).join("")
  return `<div class="flow"><div class="outline">${outline}</div>` +
    `<div class="wire"><span>${esc(s.request)}</span><span class="line">${pkts}</span><span>${esc(s.model)}</span></div>` +
    `<div class="doc-card"><div class="title">overview.md</div><span class="stamp">${esc(s.done)}</span>${sections}</div></div>`
}

function words(text) {
  return text.split(" ").map((w, i) => `<span class="w" style="--w:${i}">${esc(w)}</span>`).join(" ")
}

function renderAsk(s) {
  const passages = s.passages.map((p, i) => `<li style="--i:${i}"><span>${i + 1}</span>${esc(p)}</li>`).join("")
  return `<div class="ask"><div><p class="q"><span class="who">You</span>${words(s.question)}</p>` +
    `<span class="who search">4 closest passages</span><ol class="passages">${passages}</ol></div>` +
    `<div><span class="who answer-who">CodeDocAI</span><p class="answer">${words(s.answer)}</p>` +
    `<div class="cites">${s.cites.map((c, i) => `<span class="cite" style="--i:${i}">${esc(c)}</span>`).join("")}</div>` +
    `<p class="note">${esc(s.note)}</p></div></div>`
}

const RENDER = { parse: renderParse, draft: renderDraft, overview: renderOverview, ask: renderAsk }

export default function (component) {
  const { data, parentElement } = component
  const tour = parentElement.querySelector(".tour")
  const list = parentElement.querySelector(".steps")
  const panel = parentElement.querySelector(".panel")
  const stageDesc = parentElement.querySelector(".stage-desc")
  const pp = parentElement.querySelector(".pp")
  if (!tour || tour.dataset.ready) return
  tour.dataset.ready = "1"
  const stages = data.stages || []
  const still = window.matchMedia("(prefers-reduced-motion: reduce)").matches
  tour.style.setProperty("--stage-ms", `${data.stage_ms || 6500}ms`)

  // Why it is paused; it plays only when none of these hold.
  const holds = { held: false, offscreen: true }
  function sync() {
    tour.classList.toggle("paused", Object.values(holds).some(Boolean))
    pp.classList.toggle("is-held", holds.held)
    pp.textContent = holds.held ? "Play" : "Pause"
    pp.setAttribute("aria-label", holds.held ? "Play the walkthrough" : "Pause the walkthrough")
  }

  let current = 0
  const buttons = stages.map((s, i) => {
    const b = document.createElement("button")
    b.type = "button"
    b.className = "step"
    b.setAttribute("role", "tab")
    b.id = `tour-step-${i}`
    b.title = `Go to ${s.label}`
    b.innerHTML = `<span class="node">0${i + 1}</span><span class="rail" aria-hidden="true"><i></i></span>` +
      `<span class="text"><span class="name">${esc(s.label)}</span><span class="fig">${esc(s.figure)}</span>` +
      `<span class="desc"><span>${esc(s.caption)}</span></span></span>`
    b.addEventListener("click", () => show(i))
    b.addEventListener("keydown", (e) => {
      const step = { ArrowDown: 1, ArrowRight: 1, ArrowUp: -1, ArrowLeft: -1 }[e.key]
      if (!(e.key === "Home" || e.key === "End" || step)) return
      e.preventDefault()
      const next = e.key === "Home" ? 0 : e.key === "End" ? stages.length - 1 : (current + step + stages.length) % stages.length
      show(next)
      buttons[next].focus()
    })
    list.append(b)
    return b
  })

  // The active step's progress (its rail, or the ring on the last step) ends -> next step, looping.
  tour.addEventListener("animationend", (e) => {
    if (!tour.classList.contains("playing")) return
    if (e.animationName !== "fill" && e.animationName !== "fill-x" && e.animationName !== "ring") return
    show((current + 1) % stages.length)
  })

  function show(i) {
    current = i
    buttons.forEach((b, k) => {
      b.setAttribute("aria-selected", String(k === i))
      b.tabIndex = k === i ? 0 : -1
      b.classList.toggle("done", k < i)
      const fill = b.querySelector(".rail i")
      fill.style.animation = "none"; void fill.offsetWidth; fill.style.animation = ""
      const node = b.querySelector(".node")
      node.style.animation = "none"; void node.offsetWidth; node.style.animation = ""
    })
    panel.setAttribute("aria-labelledby", buttons[i].id)
    panel.classList.remove("anim"); void panel.offsetWidth
    panel.innerHTML = RENDER[stages[i].key](stages[i])
    stageDesc.textContent = stages[i].caption
    if (!still) panel.classList.add("anim")
  }

  show(0)
  if (still) return

  pp.hidden = false
  pp.addEventListener("click", () => { holds.held = !holds.held; sync() })
  sync()
  // Starts from the first step the first time it is on screen; pauses whenever it scrolls away.
  let started = false
  new IntersectionObserver((entries) => {
    holds.offscreen = !entries[entries.length - 1].isIntersecting
    if (!holds.offscreen && !started) { started = true; tour.classList.add("playing"); show(0) }
    sync()
  }, { threshold: 0.3 }).observe(tour)
}
"""

_TOUR = st.components.v2.component("codedocai_pipeline_tour", html=_HTML, css=_CSS, js=_JS)

STAGES = [
    {
        "key": "parse",
        "label": "Scan",
        "figure": "5 files · 23 functions",
        "caption": "Python’s ast module reads every .py file and lists each function, method and class. "
                   "Nothing is imported or run.",
        "tally": [("5", "files"), ("23", "functions"), ("0", "documented")],
        "done": "✓ ready to draft",
        "files": [
            {"path": "domain.py", "count": 2, "functions": ["get_domain_name", "get_sub_domain_name"]},
            {"path": "general.py", "count": 7, "functions": ["create_project_dir", "write_file", "file_to_set", "set_to_file", "+3"]},
            {"path": "link_finder.py", "count": 4, "functions": ["__init__", "handle_starttag", "page_links", "error"]},
            {"path": "main.py", "count": 4, "functions": ["create_workers", "work", "create_jobs", "crawl"]},
            {"path": "spider.py", "count": 6, "functions": ["boot", "crawl_page", "gather_links", "add_links_to_queue", "+2"]},
        ],
    },
    {
        "key": "draft",
        "done": "✓ 3 of 23 shown · written into a copy of your files",
        "label": "Draft",
        "figure": "23 docstrings · no API call",
        "caption": "Our fine-tuned CodeT5 writes a one-line docstring for each function, then CodeDocAI writes "
                   "them into a copy of your files. These are its real drafts for the sample.",
        "functions": [
            {"name": "get_domain_name", "def": "def get_domain_name(url):", "indent": 4, "doc": '"""Return the domain name for the given URL."""',
             "body": ["    results = get_sub_domain_name(url).split('.')"]},
            {"name": "create_project_dir", "def": "def create_project_dir(directory):", "indent": 4, "doc": '"""Create a project directory."""',
             "body": ["    if not os.path.exists(directory):"]},
            {"name": "file_to_set", "def": "def file_to_set(file_name):", "indent": 4, "doc": '"""Convert a file to a set."""',
             "body": ["    results = set()"]},
        ],
    },
    {
        "key": "overview",
        "label": "Map",
        "figure": "1 cloud request",
        "caption": "An outline of every file (names and docstring first lines, never whole files) goes to Gemini "
                   "in one request, which writes the repository overview.",
        "outline": [
            ("domain.py", "get_domain_name, get_sub_domain_name"),
            ("general.py", "create_project_dir, write_file, …"),
            ("link_finder.py", "LinkFinder.page_links, …"),
            ("main.py", "create_workers, work, crawl"),
            ("spider.py", "Spider.crawl_page, …"),
        ],
        "request": "outline only",
        "model": "Gemini · Groq as backup",
        "sections": ["What it does", "How it’s organised", "Where to start"],
        "done": "✓ written",
    },
    {
        "key": "ask",
        "label": "Ask",
        "figure": "4 passages per answer",
        "caption": "Each question is matched to the four closest functions in the index, and the answer cites "
                   "the ones it used.",
        "question": "How does the crawler avoid visiting a page twice?",
        "passages": ["Spider.crawl_page", "Spider.add_links_to_queue", "Spider.update_files", "main.work"],
        "answer": "crawl_page skips any URL already in Spider.crawled, then moves each crawled URL out of the "
                  "queue. add_links_to_queue drops links that are already queued, already crawled or off the "
                  "site’s domain.",
        "cites": ["spider.py · Spider.crawl_page", "spider.py · Spider.add_links_to_queue"],
        "note": "An example of the answer format, written for this page.",
    },
]


def render() -> None:
    _TOUR(key="pipeline_tour", data={"stages": STAGES, "stage_ms": STAGE_MS}, width="stretch")
