"""
screens/landing.py -- CodeDocAI
Landing screen renderer (Session 1 + visual polish pass).
"""

import streamlit as st


def render_landing() -> None:
    # Masthead: 3-column split
    col_logo, col_pill, col_btn = st.columns([6, 1.8, 1.8], vertical_alignment="center")

    with col_logo:
        st.markdown('<div class="masthead-wordmark" style="margin-top: 4px;">CodeDocAI</div>', unsafe_allow_html=True)
    with col_pill:
        st.markdown('<div style="display: flex; justify-content: flex-end; margin-top: 4px;"><span class="scan-ready-pill">PIPELINE READY</span></div>', unsafe_allow_html=True)
    with col_btn:
        st.markdown('<div id="masthead-how-it-works"></div>', unsafe_allow_html=True)
        if st.button("HOW IT WORKS", key="cta_how_it_works"):
            st.session_state["current_screen"] = "architecture"
            st.rerun()

    # Replaced inline style with existing CSS token class
    st.markdown('<hr class="nav-rail-divider">', unsafe_allow_html=True)

    # ---- Hero: two-column (text left, code-editor mockup right) ----
    col_hero_text, col_hero_vis = st.columns([1.2, 1], gap="large")
    with col_hero_text:
        st.markdown(
            '<div class="hero">'
            '<div class="hero-headline typewriter-headline">Every function has a story worth documenting.</div>'
            '<div class="hero-subhead cascade-fade" style="animation-delay: 1.2s;">'
            'Provide a public GitHub repository URL or upload a .zip archive. It drafts '
            'docstrings, writes a module overview, and answers questions about '
            'the code\u2009\u2014\u2009grounded in what\u2019s actually there, not a guess.'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div id="hero-cta-marker"></div>', unsafe_allow_html=True)
        if st.button("START A SCAN", key="cta_hero"):
            st.session_state["current_screen"] = "scan"
            st.rerun()

    with col_hero_vis:
        mock_editor_html = """
    <div class="mock-editor cascade-fade" style="animation-delay: 1.4s;">
        <div class="mock-editor-bar">
            <span class="dot" style="background:#E5484D"></span>
            <span class="dot" style="background:#E8B339"></span>
            <span class="dot" style="background:#4CAF50"></span>
            <span class="filename">parser.py</span>
        </div>
        <div class="mock-editor-body">
            <div class="mock-line"><span class="mock-editor-lineno">1</span><span class="code-kw">def</span> parse_functions(tree):</div>
            <div class="mock-line"><span class="mock-editor-lineno">2</span>    <span class="anim-typewriter">\"\"\" Walk an AST and return every function node. \"\"\"</span></div>
            <div class="mock-line"><span class="mock-editor-lineno">3</span>    <span class="code-kw">return</span> [n <span class="code-kw">for</span> n <span class="code-kw">in</span> ast.walk(tree)</div>
            <div class="mock-line"><span class="mock-editor-lineno">4</span>            <span class="code-kw">if</span> isinstance(n, ast.FunctionDef)]</div>
        </div>
        <div class="mock-editor-status">
            <span class="anim-status"></span>
        </div>
    </div>
    """
        st.markdown(mock_editor_html, unsafe_allow_html=True)

    # ---- Security Bar & Rationale Grid ----
    st.markdown(
        """
        <div class="security-bar cascade-fade" style="animation-delay: 1.6s;">
            <div class="security-item">
                <h4>LOCAL AST PARSING</h4>
                <p>Code is parsed ephemerally. No source files are written to disk.</p>
            </div>
            <div class="security-item">
                <h4>ZERO RETENTION</h4>
                <p>Repositories are dumped immediately after the ChromaDB vectorization is complete.</p>
            </div>
            <div class="security-item">
                <h4>API ISOLATION</h4>
                <p>Gemini RAG requests are stateless and scoped strictly to your session context.</p>
            </div>
        </div>

        <div class="why-section cascade-fade" style="animation-delay: 1.8s;">
            <div class="section-label">RATIONALE</div>
            <div class="rationale-grid">
                <div class="rationale-col">
                    <h3>THE REALITY</h3>
                    <p class="why-body">Functions ship without docstrings. Modules lack overviews. Context is lost the moment the author switches tasks. Inheriting undocumented code means reading it line-by-line.</p>
                </div>
                <div class="rationale-col">
                    <h3>THE SHIFT</h3>
                    <p class="why-body">CodeDocAI establishes an automated documentation baseline. It drafts the first pass of functional specs and module reasoning automatically, so you review rather than write.</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---- Unified Process + Built-With card ----
    _PROCESS_STEPS = [
        ("01", "SCAN",
         "Python\u2019s ast module walks every function and class, flagging what\u2019s undocumented."),
        ("02", "DRAFT",
         "A fine-tuned CodeT5 model writes a docstring for each one."),
        ("03", "SYNTHESIZE",
         "Agents reason across the file to write a module-level overview."),
        ("04", "ASK",
         "Ask questions in plain English\u2009\u2014\u2009answers are grounded in the real code, not a guess."),
    ]
    _TAGS = ["CodeT5-small", "CrewAI", "ChromaDB", "Gemini API", "RAG", "Python ast"]

    card_html = (
        '<div class="process-card cascade-fade" style="animation-delay: 2.0s;">'
        '<div class="section-label">THE PROCESS</div>'
        '<div class="timeline">'
    )
    for idx, step, desc in _PROCESS_STEPS:
        card_html += (
            f'<div class="timeline-item">'
            f'  <div class="timeline-left">'
            f'    <span class="timeline-index">{idx}</span>'
            f'    <span class="timeline-step">{step}</span>'
            f'  </div>'
            f'  <span class="timeline-desc">{desc}</span>'
            f'</div>'
        )
    card_html += '</div>'  # end .timeline
    card_html += '<div class="card-built-label">BUILT WITH</div>'
    card_html += '<div class="built-tags">'
    for tag in _TAGS:
        card_html += f'<span class="built-tag">{tag}</span>'
    card_html += '</div></div>'  # end .built-tags + .process-card
    st.markdown(card_html, unsafe_allow_html=True)

    # ---- Capabilities Grid ----
    st.markdown(
        """
        <div class="caps-grid cascade-fade" style="animation-delay: 2.2s;">
            <div class="caps-item">
                <h4>Semantic RAG Queries</h4>
                <p>Ask complex architectural questions. Answers cite specific line numbers and generated docstrings.</p>
            </div>
            <div class="caps-item">
                <h4>Edge-Case Resilient</h4>
                <p>Successfully ignores nested functions inside list comprehensions and correctly maps complex *args and **kwargs.</p>
            </div>
            <div class="caps-item">
                <h4>Agentic Overviews</h4>
                <p>CrewAI agents debate the module's broader purpose, creating holistic overviews rather than just isolated function summaries.</p>
            </div>
            <div class="caps-item">
                <h4>Frictionless Export</h4>
                <p>Archive a complete .md documentation manifest alongside your Q&A transcript in a single, locally compiled ZIP.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---- Closing CTA (tight spacing, no extra margin) ----
    st.markdown(
        '<div class="closing-section cascade-fade" style="animation-delay: 2.4s;">'
        '<div class="closing-label">Initialize a scan on a local or remote repository.</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div id="footer-cta-marker"></div>', unsafe_allow_html=True)
    if st.button("START A SCAN", key="cta_closing"):
        st.session_state["current_screen"] = "scan"
        st.rerun()
