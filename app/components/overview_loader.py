"""
The Generate screen's last step: while the cloud model writes the repository
overview (one request, often 10-30 seconds), a loading screen in the same
pattern as the CodeT5 one (mark, title, rotating lines, bar, note) replaces
the log, so the page never looks stuck. Styles live in styles.py (.ovl-*).

Everything moves on one loop of CYCLE_MS: the mark writes its three lines by
2.6 s and the bar fills by 3.0 s, then both hold still until the loop ends;
the rotating lines change just after a loop starts. The screen waits for that
still end before moving on (wait_for_cycle_end), so the animation is never
cut mid-way. Under prefers-reduced-motion it is a still picture.
"""

import html
import time

import streamlit as st

CYCLE_MS = 3600   # one loop of the mark and the bar
REST_MS = 600     # the end of each loop, where everything is finished and still
RERUN_LAG = 0.25  # measured: the next screen appears about this long after the server moves on
# Leaving at 3.15 s into a loop puts the switch at about 3.4 s, inside the rest (3.0-3.6 s).
LEAVE_AT = (CYCLE_MS - REST_MS) / 1000 + 0.15
LEAVE_SLACK = 0.15


def loader_html(file_count: int) -> str:
    files = f"{file_count} file{'s' if file_count != 1 else ''}"
    lines = (
        f"Sending an outline of {files} to Gemini…",
        "Working out what each module is for…",
        "Tracing how the modules call each other…",
        "Choosing where a newcomer should start…",
    )
    spans = "".join(f"<span>{html.escape(line)}</span>" for line in lines)
    return (
        '<div class="ovl" role="status" aria-live="polite">'
        '<div class="ovl-mark" aria-hidden="true"><span class="ovl-line"></span>'
        '<span class="ovl-line"></span><span class="ovl-line"></span></div>'
        '<p class="ovl-title">Writing your overview</p>'
        f'<p class="ovl-chip" aria-hidden="true">{html.escape(files)} · outline only → overview.md</p>'
        f'<p class="ovl-lines" aria-hidden="true">{spans}</p>'
        '<span class="sr-only">Writing the repository overview with the cloud model.</span>'
        '<div class="ovl-bar" aria-hidden="true"><span></span></div>'
        '<p class="ovl-note">One request to Gemini · Groq steps in if it is busy</p>'
        '</div>'
    )


def render(py_files: list[str]) -> float:
    """Shows the loader where it is called and returns when it started (time.monotonic())."""
    st.html(loader_html(len(py_files)))
    return time.monotonic()


def wait_for_cycle_end(started: float) -> float:
    """Sleeps until the switch to the next screen lands in a loop's still end; returns the wait."""
    wait = cycle_wait(time.monotonic() - started)
    time.sleep(wait)
    return wait


def cycle_wait(elapsed: float) -> float:
    """
    Seconds to wait, ``elapsed`` seconds after the loader started, before leaving the screen.

    The page only changes a moment after the server moves on (RERUN_LAG), so the server
    leaves at LEAVE_AT into a loop and the switch lands in the rest. At least one full
    loop always plays, so a fast answer still reads as finished work.
    """
    cycle = CYCLE_MS / 1000
    if elapsed < LEAVE_AT:
        return LEAVE_AT - elapsed
    into_cycle = elapsed % cycle
    if LEAVE_AT - 1e-9 <= into_cycle <= LEAVE_AT + LEAVE_SLACK + 1e-9:  # float-safe bounds
        return 0.0
    return (LEAVE_AT - into_cycle) % cycle
