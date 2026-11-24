"""
screens/landing.py -- CodeDocAI
The home page. The shared top bar (wordmark, How it works, sign-in) is drawn by
app.py above every screen; its "How it works" link scrolls to #how-it-works here.

The figures come from real runs of the full pipeline with CodeDocAI's own
CodeT5 model (see BENCHMARK below). The try-it box runs that model live.
"""

import html
import re

import streamlit as st

from backend.tryit import SnippetError, draft_snippet
from components import code_window, pipeline_tour

HEADLINE = "Docstrings for the functions nobody got around to documenting."

# ---------------------------------------------------------------- measured figures

# Two full pipeline runs (scan, CodeT5 drafting, indexing) on a CPU, no GPU, 2026-11-24:
#   scrapy/scrapy          195 files, 1,979 functions, 1,000 drafted (the per-scan cap), 24% -> 74%, 265.1 s
#   buckyroberts/Spider      5 files,    23 functions,    23 drafted, 0% -> 100%, 5.2 s
# 1,023 drafts in 270.2 s is 0.26 s each, parsing and indexing included.
BENCHMARK_NOTE = "Measured on scrapy/scrapy and buckyroberts/Spider · full pipeline on a CPU, no GPU"
BENCHMARK = [
    ("1,023", "docstrings drafted"),
    ("2,002", "functions scanned"),
    ("24% → 74%", "scrapy’s coverage, one scan"),
    ("0.26 s", "per docstring, end to end"),
    ("0", "API calls to draft them"),
]

# ---------------------------------------------------------------- try it

_SAMPLES = {
    "gather_links": '''def gather_links(page_url):
    html_string = ''
    try:
        response = urlopen(page_url)
        if 'text/html' in response.getheader('Content-Type'):
            html_bytes = response.read()
            html_string = html_bytes.decode("utf-8")
        finder = LinkFinder(Spider.base_url, page_url)
        finder.feed(html_string)
    except Exception as e:
        print(str(e))
        return set()
    return finder.page_links()
''',
    "add_links_to_queue": '''def add_links_to_queue(links):
    for url in links:
        if (url in Spider.queue) or (url in Spider.crawled):
            continue
        if Spider.domain_name != get_domain_name(url):
            continue
        Spider.queue.add(url)
''',
    "crawl": '''def crawl():
    queued_links = file_to_set(QUEUE_FILE)
    if len(queued_links) > 0:
        print(str(len(queued_links)) + ' links in the queue')
        create_jobs()
''',
}

# ---------------------------------------------------------------- what you get

# Icons are CSS masks in styles.py (.get-icon-*): st.html's sanitizer drops inline SVG.

_TAKEAWAYS = [
    ("folder", "documented_source/", "Your files with every drafted docstring written in. Your repository itself is never changed.",
     "5 files · 23 docstrings"),
    ("diff", "docstrings.patch", "The same change as a unified diff, for git apply and a normal code review.", "+23 lines"),
    ("chart", "coverage_report.md", "Coverage before and after, per file, ready to paste into a pull request.", "0% → 100%"),
    ("doc", "documentation.md", "The repository overview and every docstring in one readable file.", "1 file to share"),
]

# ---------------------------------------------------------------- privacy

_SERVER = ["Reads your code with ast; never runs it", "Drafts every docstring with our CodeT5",
           "Keeps the search index in memory", "Deletes its copy when generation ends"]
_CLOUD = [("One outline per scan", "names and docstring first lines, not whole files"),
          ("Each question", "with the four passages it was matched to"),
          ("Function source", "only if our model is down and the cloud drafts instead")]

# ---------------------------------------------------------------- questions

_FAQ = [
    ("Does CodeDocAI run my code?",
     "No. Python’s ast module reads each file as text. Nothing is imported or executed."),
    ("Which languages does it support?",
     "Python only. A repository without .py files is turned away when you scan it."),
    ("Does drafting use ChatGPT or Gemini?",
     "No. Docstrings come from our own CodeT5 model, fine-tuned for this job. Only the repository "
     "overview and your questions go to Gemini, with Groq as the backup."),
    ("Where does my code go, and for how long?",
     "To CodeDocAI’s server for the scan. The copy is deleted as soon as generation finishes; "
     "only the results stay in your session."),
    ("How large a repository can it handle?",
     "Up to 100 MB, from GitHub or a .zip, with up to 1,000 functions drafted per scan."),
    ("Will it change my repository?",
     "No. You download a .zip with documented copies and a patch, and choose what to apply."),
]

# ---------------------------------------------------------------- markup helpers

_KEYWORDS = {
    "False", "None", "True", "and", "as", "assert", "async", "await", "break", "class", "continue",
    "def", "del", "elif", "else", "except", "finally", "for", "from", "global", "if", "import", "in",
    "is", "lambda", "nonlocal", "not", "or", "pass", "raise", "return", "try", "while", "with", "yield",
}
_BUILTINS = {"len", "str", "int", "float", "dict", "list", "set", "tuple", "print", "open", "range"}
_TOKEN = re.compile(r'("{3}.*?"{3}|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|#.*$|@\w+|\b\d+(?:\.\d+)?\b|\b[A-Za-z_]\w*\b)')


def highlight(line: str) -> str:
    """One line of Python as escaped HTML with the token classes the code window uses."""
    out, last, previous = [], 0, ""
    for match in _TOKEN.finditer(line):
        token = match.group(0)
        out.append(html.escape(line[last:match.start()]))
        if token.startswith("#"):
            cls = "tk-comment"
        elif token[0] in "\"'":
            cls = "tk-string"
        elif token.startswith("@"):
            cls = "tk-decorator"
        elif token[0].isdigit():
            cls = "tk-number"
        elif previous in ("def", "class"):
            cls = "tk-name"
        elif token in _KEYWORDS:
            cls = "tk-keyword"
        elif token in _BUILTINS:
            cls = "tk-builtin"
        else:
            cls = ""
        out.append(f'<span class="{cls}">{html.escape(token)}</span>' if cls else html.escape(token))
        if token[0].isalpha() or token[0] == "_":
            previous = token
        last = match.end()
    out.append(html.escape(line[last:]))
    return "".join(out)


def code_lines(lines: list[str], added: set[int] = frozenset()) -> str:
    """Numbered, highlighted lines; the indexes in ``added`` are marked as new."""
    rows, order = [], 0
    for index, line in enumerate(lines):
        cls, style = "ln", ""
        if index in added:
            cls, style = "ln ln-add", f' style="--a:{order}"'
            order += 1
        rows.append(f'<span class="{cls}"{style}><span class="ln-no" aria-hidden="true">{index + 1}</span>'
                    f'{highlight(line) or " "}</span>')
    return "".join(rows)


def _typed(text: str) -> str:
    """The headline as one span per character, so CSS can type it out.

    Characters sit inside a span per word, so lines break where the finished
    headline breaks and nothing reflows while it types. ``--c`` is the
    character's position in the whole headline, spaces included.
    """
    words, c = [], 0
    for word in text.split():
        chars = []
        for ch in word:
            chars.append(f'<span class="hero-char" style="--c:{c}">{ch}</span>')
            c += 1
        words.append(f'<span class="hero-word">{"".join(chars)}</span>')
        c += 1  # the space
    return " ".join(words) + '<span class="hero-caret" aria-hidden="true"></span>'


def _heading(kicker: str, title: str, sub: str, anchor: str) -> str:
    return (f'<p class="home-kicker">{kicker}</p>'
            f'<h2 class="landing-h2 home-title" id="{anchor}">{title}</h2>'
            + (f'<p class="home-sub">{sub}</p>' if sub else ""))


# ---------------------------------------------------------------- sections

def _stats() -> str:
    cells = "".join(
        f'<div class="stat" role="listitem"><span class="stat-value">{html.escape(value)}</span>'
        f'<span class="stat-label">{label}</span></div>'
        for value, label in BENCHMARK
    )
    return (
        '<section class="home-stats home-reveal" aria-label="Measured results">'
        f'<div class="stat-row count-up" role="list">{cells}</div>'
        f'<p class="home-note">{BENCHMARK_NOTE}</p>'
        '</section>'
    )


def _how_heading() -> str:
    return ('<section class="home-section home-reveal how" aria-labelledby="how-it-works">'
            + _heading("How it works", "From bare code to answers in four steps",
                       "It plays on a loop; click any step to jump to it. Every name and draft is from a real scan.", "how-it-works")
            + '</section>')


def _takeaways() -> str:
    cards = "".join(
        '<article class="get-card home-card">'
        f'<span class="get-icon get-icon-{icon}" aria-hidden="true"></span>'
        f'<h3 class="get-name">{name}</h3><p class="get-desc">{desc}</p>'
        f'<span class="get-badge">{badge}</span>'
        '</article>'
        for icon, name, desc, badge in _TAKEAWAYS
    )
    return (
        '<section class="home-section home-reveal takeaways" aria-labelledby="takeaways-h">'
        + _heading("What you get", "Every scan ends in one .zip you can commit",
                   "Badges show what the Spider sample produced.", "takeaways-h")
        + f'<div class="get-grid">{cards}</div></section>'
    )


def _privacy() -> str:
    server = "".join(f"<li>{item}</li>" for item in _SERVER)
    cloud = "".join(f'<li><span class="priv-item">{head}</span><span class="priv-detail">{detail}</span></li>'
                    for head, detail in _CLOUD)
    return (
        '<section class="home-section home-reveal privacy" aria-labelledby="privacy-h">'
        + _heading("Privacy", "What a third-party AI gets to see",
                   "Docstrings never need one. Two later steps do, and keys and tokens are "
                   "redacted before either request leaves.", "privacy-h")
        + '<div class="flowmap">'
          '<div class="node node-repo"><span class="node-label">Your repository</span>'
          '<span class="node-sub">GitHub URL or .zip</span></div>'
          '<div class="pipe-link" aria-hidden="true"><span></span></div>'
          '<div class="node node-server home-card"><span class="node-label">CodeDocAI server</span>'
          f'<ul class="node-list">{server}</ul></div>'
          '<div class="pipe-link pipe-link-gate" aria-hidden="true"><span></span><em>secrets redacted</em></div>'
          '<div class="node node-cloud home-card"><span class="node-label">Gemini · Groq as backup</span>'
          f'<ul class="node-list node-list-cloud">{cloud}</ul></div>'
          '</div></section>'
    )


def _faq() -> str:
    items = "".join(f'<details class="faq"><summary>{q}</summary><p>{a}</p></details>' for q, a in _FAQ)
    return (
        '<section class="home-section home-reveal faq-section" aria-labelledby="faq-h">'
        '<div class="faq-intro">'
        + _heading("FAQ", "Before you scan", "The short answers to what people ask first.", "faq-h")
        + '</div>'
        f'<div class="faq-list">{items}</div></section>'
    )


# ---------------------------------------------------------------- try it

def _use_sample() -> None:
    choice = st.session_state.get("tryit_sample")
    if choice:
        st.session_state["tryit_code"] = _SAMPLES[choice]
    st.session_state.pop("tryit_result", None)


def _result_panel(result: dict | None, error: str | None) -> str:
    if error:
        body = f'<p class="try-empty try-error" role="alert">{html.escape(error)}</p>'
        note = ""
    elif result:
        lines = result["source"].split("\n")
        drafted = {doc.strip() for _, doc in result["drafts"]}
        added = {i for i, line in enumerate(lines) if line.strip().strip('"') in drafted}
        body = f'<pre class="pane-code try-code">{code_lines(lines, added)}</pre>'
        count = len(result["drafts"])
        note = (f'<span class="try-meta">{count} docstring{"s" if count != 1 else ""} drafted in '
                f'{result["seconds"]:.2f} s by CodeT5-small · no API call</span>')
    else:
        body = '<p class="try-empty">The documented version appears here.</p>'
        note = ""
    return (f'<figure class="code-pane try-out{" has-result" if result else ""}">'
            '<figcaption><span class="pane-tab">snippet.py</span>'
            f'<span class="pane-note">{"documented" if result else "waiting"}</span></figcaption>'
            f'{body}</figure>{note}')


@st.fragment
def _try_it() -> None:
    st.session_state.setdefault("tryit_code", _SAMPLES["gather_links"])
    with st.container(key="tryit"):
        st.html(_heading("Try it", "Watch our model document a function",
                         "Paste any Python function or pick a sample. CodeT5 drafts its docstring in about "
                         "a second, with no API call.", "try-h"))
        left, right = st.columns(2, gap="medium")
        with left:
            st.segmented_control("Sample", options=list(_SAMPLES), key="tryit_sample", on_change=_use_sample,
                                 label_visibility="collapsed")
            st.text_area("Python function", key="tryit_code", height=280, max_chars=4000,
                         label_visibility="collapsed")
            if st.button("Draft the docstring", key="tryit_go", icon=":material/auto_awesome:"):
                try:
                    st.session_state["tryit_result"] = draft_snippet(
                        st.session_state.get("ai_engine"), st.session_state["tryit_code"])
                except SnippetError as error:
                    st.session_state["tryit_result"] = str(error)
        with right:
            result = st.session_state.get("tryit_result")
            st.html(_result_panel(result if isinstance(result, dict) else None,
                                  result if isinstance(result, str) else None))


# ---------------------------------------------------------------- page

def render_landing() -> None:
    # ---- Hero: text left, editor right ----
    col_hero_text, col_hero_vis = st.columns([1.2, 1], gap="large", vertical_alignment="center")
    with col_hero_text:
        st.markdown(
            '<div class="hero">'
            f'<h1 class="hero-headline" aria-label="{HEADLINE}">{_typed(HEADLINE)}</h1>'
            '<p class="hero-subhead hero-after">Our fine-tuned model drafts the missing docstrings, writes them '
            'into your files, and answers questions about the code with citations.</p>'
            '</div>',
            unsafe_allow_html=True,
        )
        with st.container(key="hero_cta"):
            start = st.button("Start a scan", key="cta_hero", type="primary")
        if start:
            st.session_state["current_screen"] = "scan"
            st.rerun()

    with col_hero_vis, st.container(key="hero_window"):
        code_window.render()

    st.html(_stats())
    _try_it()
    st.html(_how_heading())
    with st.container(key="how_tour"):
        pipeline_tour.render()
    st.html(_takeaways() + _privacy() + _faq())

    # ---- Closing CTA ----
    st.markdown(
        '<div class="closing-section"><p class="closing-label">Scan a repository from GitHub or a .zip.</p></div>',
        unsafe_allow_html=True,
    )
    with st.container(horizontal=True, horizontal_alignment="center", key="closing_cta"):
        if st.button("Start a scan", key="cta_closing", type="secondary"):
            st.session_state["current_screen"] = "scan"
            st.rerun()
