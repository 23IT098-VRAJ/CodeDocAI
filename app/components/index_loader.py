"""
The Generate screen's Index step: while the functions are embedded for search,
a ring fills to the real percentage (entries embedded / entries in total) and
playful lines rotate under it. Styles live in styles.py (.ixl-*).

The screen redraws this after every batch, which would restart a plain CSS
animation each time. So each redraw carries where it left off: the ring
animates from the previous percentage to the new one (--from, --to), and the
looping parts start at a negative delay equal to the time spent indexing so
far (--t), which makes them look continuous across redraws.
"""

import html


def index_loader_html(done: int, total: int, previous_pct: float, elapsed: float) -> str:
    pct = 100 * done / total if total else 100
    lines = (
        f"Shelving {total:,} entries by what they do…",
        "Giving every docstring a library card…",
        "Teaching the index which words mean the same thing…",
        "Lining up answers for your first question…",
    )
    spans = "".join(f"<span>{html.escape(line)}</span>" for line in lines)
    return (
        f'<div class="ixl" role="status" aria-live="polite" '
        f'style="--from:{previous_pct:.1f}%;--to:{pct:.1f}%;--t:-{elapsed:.2f}s">'
        '<div class="ixl-ring" aria-hidden="true">'
        '<span class="ixl-orbit"><i></i><i></i><i></i></span>'
        f'<span class="ixl-pct">{pct:.0f}<small>%</small></span>'
        '</div>'
        '<p class="ixl-title">Indexing for questions</p>'
        f'<p class="ixl-chip">{done:,} of {total:,} entries · on this server, no API calls</p>'
        f'<p class="ixl-lines" aria-hidden="true">{spans}</p>'
        f'<span class="sr-only">Indexing for questions: {pct:.0f} percent.</span>'
        '</div>'
    )
