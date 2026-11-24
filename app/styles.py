"""
styles.py -- CodeDocAI
Single source of truth for all CSS design tokens and component styles.
Call inject_css() exactly once, immediately after st.set_page_config().
"""

import streamlit as st


def inject_css() -> None:
    """
    Inject the application's entire CSS block.

    st.html sends HTML that holds only a <style> tag to Streamlit's event container,
    outside the page: it takes no space, and the CSS text no longer becomes part of
    the main landmark's accessible name (st.markdown rendered it inside <main>).
    Never write an HTML tag inside the CSS, even in a comment: the sanitizer then
    drops the whole style block.
    """
    st.html(
        """
    <style>
    /* Fonts load through the theme in .streamlit/config.toml. */

    /* ================================================================
       DESIGN TOKENS -- three layers.
       1. Primitives hold the raw values and carry no meaning.
       2. Semantic tokens say what a value is for; change these to re-theme.
       3. Component tokens let one component be tuned without touching the rest.
       Rules below read layers 2 and 3. A raw colour, size or duration in a
       rule is a bug, apart from the optical nudges marked as such.
       ================================================================ */

    /* === 1. PRIMITIVES === */
    :root {
        /* colour */
        --color-black:      #000000;
        --color-ink-950:    #050505;
        --color-ink-900:    #0A0A0A;
        --color-ink-850:    #111111;
        --color-ink-800:    #121212;
        --color-ink-750:    #151515;
        --color-ink-700:    #222222;
        --color-ink-500:    #5E5E5E;
        --color-grey-400:   #A0A0A0;
        --color-sand-400:   #A59C8A;
        --color-sand-100:   #F0EAD9;
        --color-white:      #FFFFFF;
        --color-amber-400:  #F0C35A;
        --color-amber-500:  #E8B339;
        --color-red-500:    #E5484D;
        --color-green-500:  #4CAF50;
        /* the same hues as channels, for translucent washes */
        --rgb-white:  255, 255, 255;
        --rgb-black:  0, 0, 0;
        --rgb-amber:  232, 179, 57;
        --rgb-green:  76, 175, 80;

        /* type families */
        --font-mono:   'IBM Plex Mono', monospace;
        --font-serif:  'Fraunces', Georgia, serif;

        /* spacing: 4px base; the "h" steps are half steps */
        --space-0h: 2px;
        --space-1:  4px;
        --space-1h: 6px;
        --space-2:  8px;
        --space-2h: 12px;
        --space-3:  16px;
        --space-4:  24px;
        --space-5:  32px;
        --space-6:  48px;

        /* radius */
        --radius-xs:    2px;
        --radius-sm:    4px;
        --radius-base:  8px;
        --radius-md:    12px;
        --radius-lg:    16px;
        --radius-pill:  999px;

        /* type scale: 12 / 14 / 16 / 18 / 20 / 24 / 32 / 40. Nothing below 12px. */
        --text-xs:    0.75rem;
        --text-sm:    0.875rem;
        --text-base:  1rem;
        --text-md:    1.125rem;
        --text-lg:    1.25rem;
        --text-xl:    1.5rem;
        --text-2xl:   2rem;
        --text-3xl:   2.5rem;

        /* line height */
        --leading-none:     1;
        --leading-tight:    1.1;
        --leading-snug:     1.35;
        --leading-normal:   1.5;
        --leading-relaxed:  1.65;

        /* letter spacing, in em so it scales with the text */
        --tracking-tighter: -0.03em;
        --tracking-tight:   -0.02em;
        --tracking-snug:    -0.01em;
        --tracking-wide:    0.05em;
        --tracking-wider:   0.08em;
        --tracking-widest:  0.1em;
        --tracking-caps:    0.12em;

        /* motion */
        --duration-fast:    0.15s;
        --duration-normal:  0.2s;

        --opacity-disabled: 0.45;
    }

    /* === 2. SEMANTIC === */
    :root {
        /* surfaces */
        --bg:              var(--color-black);
        --surface:         var(--color-ink-900);
        --surface-sunken:  var(--color-ink-950);
        --surface-raised:  var(--color-ink-850);
        --surface-code:    var(--color-ink-800);

        /* text */
        --text-primary:      var(--color-sand-100);
        --text-muted:        var(--color-sand-400);
        --text-strong:       var(--color-white);
        --text-placeholder:  var(--color-grey-400);
        --text-on-accent:    var(--color-ink-750);

        /* lines. --border is a decorative hairline; --border-strong marks the edge
           of a control and meets the 3:1 contrast WCAG asks of interface parts. */
        --border:         var(--color-ink-700);
        --border-strong:  var(--color-ink-500);
        --border-subtle:  rgba(var(--rgb-white), 0.1);
        --border-faint:   rgba(var(--rgb-white), 0.05);

        /* brand and status */
        --accent-amber:   var(--color-amber-500);
        --accent-red:     var(--color-red-500);
        --color-success:  var(--color-green-500);
        --color-warning:  var(--accent-amber);
        --color-danger:   var(--accent-red);

        /* translucent washes over the background */
        --accent-wash-1:  rgba(var(--rgb-amber), 0.05);
        --surface-frosted: rgba(var(--rgb-black), 0.72);
        --accent-wash-2:  rgba(var(--rgb-amber), 0.06);
        --accent-wash-3:  rgba(var(--rgb-amber), 0.08);
        --accent-wash-4:  rgba(var(--rgb-amber), 0.15);
        --accent-line:    rgba(var(--rgb-amber), 0.2);
        --success-wash:   rgba(var(--rgb-green), 0.05);
        --success-line:   rgba(var(--rgb-green), 0.2);
        --neutral-wash-1: rgba(var(--rgb-white), 0.03);
        --neutral-wash-2: rgba(var(--rgb-white), 0.08);

        /* focus */
        --focus-ring-color:   var(--accent-amber);
        --focus-ring-width:   2px;
        --focus-ring-offset:  2px;
    }

    /* === 3. COMPONENT === */
    :root {
        --button-bg:             var(--accent-amber);
        --button-fg:             var(--text-on-accent);
        --button-radius:         var(--radius-md);
        --button-font-size:      var(--text-xs);
        --button-hover-opacity:  0.88;
        --button-danger-bg:      var(--color-danger);
        --button-danger-fg:      var(--text-on-accent);

        --input-bg:            var(--surface);
        --input-fg:            var(--text-primary);
        --input-placeholder:   var(--text-placeholder);
        --input-border:        var(--border-strong);
        --input-border-focus:  var(--accent-amber);
        --input-radius:        var(--radius-md);

        --card-bg:      var(--surface);
        --card-border:  var(--border);
        --card-radius:  var(--radius-md);
    }

    /* -- Global resets -- */
    html, body, [class*="css"], .stApp, .block-container {
        background-color: var(--bg) !important;
        color:            var(--text-primary) !important;
        font-family:      var(--font-mono) !important;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }

    /* -- Heading elements use Fraunces -- */
    h1, h2, h3, h4, h5, h6,
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        font-family: var(--font-serif) !important;
        color:       var(--text-primary) !important;
    }

    /* -- Container padding -- */
    .block-container {
        padding-top:    var(--space-6) !important; /* Safe, uniform top drop */
        padding-bottom: var(--space-6) !important;
        max-width: 1040px !important;
    }

    /* -- Global rule: zero box-shadow -- */
    *, *::before, *::after {
        box-shadow: none !important;
    }

    /* -- Prevent IBM Plex Mono ligature substitution -- */
    [style*="IBM Plex Mono"],
    .type-label, .swatch-name, .spacing-label, .r-label,
    .page-subtitle, .foundation-footer, .no-shadow-note,
    .scan-ready-pill, .landing-footer,
    /* Session 1b mono classes */
    .section-label, .process-index, .process-step,
    .built-tag,
    /* Session 2 mono classes */
    .scan-intro, .scan-or-label,
    .scan-error-line, .scan-summary,
    .ledger-index, .ledger-path, .ledger-meta,
    /* Session 3 mono classes */
    .gen-intro, .gen-outcome-summary,
    .gen-error-msg, .gen-outcome-label,
    /* Session 4 mono classes */
    .docs-clean-line, .docs-fn-name, .ai-draft-badge,
    .docs-docstring, .docs-empty-head, .docs-empty-sub,
    /* Session 5 mono classes */
    .qa-turn-label, .qa-q-label, .qa-a-label,
    .qa-citation-pill, .qa-chips-label,
    /* Session 6a mono classes */
    .rail-current, .rail-muted, .rail-arrow,
    .docs-jump-link, .scan-estimate-body,
    .code-kw, .code-str {
        font-feature-settings: 'liga' 0, 'calt' 0 !important;
        font-variant-ligatures: none !important;
    }

    /* -- Hide Streamlit chrome safely -- */
    #MainMenu, footer {
        visibility: hidden !important;
        height: 0 !important;
        min-height: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    /* The header is hidden but keeps its box, and lets clicks through to the page. */
    header {
        visibility: hidden !important;
        background: transparent !important;
        pointer-events: none !important;
    }
    /* ================================================================
       SESSION 0 -- Foundation verification page
       ================================================================ */

    .token-grid {
        display: flex;
        flex-wrap: wrap;
        gap: var(--space-3);
        margin: var(--space-3) 0 var(--space-5);
    }
    .swatch {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        gap: var(--space-1);
        min-width: 140px;
    }
    .swatch-block {
        width: 120px;
        height: 60px;
        border-radius: var(--radius-md);
        border: 1px solid var(--border);
    }
    .swatch-name {
        font-family: var(--font-mono);
        font-size: var(--text-xs);
        font-weight: 500;
        color: var(--text-muted);
        line-height: var(--leading-snug);
    }
    .type-specimen {
        padding: var(--space-3) 0;
        border-bottom: 1px solid var(--border);
    }
    .type-label {
        font-family: var(--font-mono);
        font-size: var(--text-xs);
        font-weight: 400;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: var(--tracking-widest);
        margin-bottom: var(--space-1);
    }
    .spacing-grid {
        display: flex;
        align-items: flex-end;
        gap: var(--space-4);
        margin: var(--space-3) 0 var(--space-5);
        flex-wrap: wrap;
    }
    .spacing-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: var(--space-1);
    }
    .spacing-bar {
        background: var(--accent-amber);
        width: 28px;
        border-radius: var(--radius-xs);
    }
    .spacing-label {
        font-family: var(--font-mono);
        font-size: var(--text-xs);
        font-weight: 400;
        color: var(--text-muted);
    }
    .radius-grid {
        display: flex;
        flex-wrap: wrap;
        gap: var(--space-4);
        margin: var(--space-3) 0 var(--space-5);
    }
    .radius-box {
        width: 110px;
        height: 64px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        border: 1px solid var(--border);
        background: var(--surface);
        gap: var(--space-1);
    }
    .radius-box .r-label {
        font-family: var(--font-mono);
        font-size: var(--text-xs);
        font-weight: 500;
        color: var(--text-muted);
    }
    .section-header {
        font-family: var(--font-serif) !important;
        font-size: var(--text-lg);
        font-weight: 600;
        color: var(--text-primary);
        margin: var(--space-5) 0 var(--space-2);
        padding-bottom: var(--space-2);
        border-bottom: 1px solid var(--border);
    }
    .page-title {
        font-family: var(--font-serif) !important;
        font-size: var(--text-2xl);
        font-weight: 700;
        color: var(--accent-amber);
        margin-bottom: var(--space-2);
        letter-spacing: var(--tracking-tight);
    }
    .page-subtitle {
        font-family: var(--font-mono);
        font-size: var(--text-sm);
        font-weight: 400;
        color: var(--text-muted);
        margin-bottom: var(--space-5);
    }
    .foundation-footer {
        font-family: var(--font-mono);
        font-size: var(--text-sm);
        font-weight: 400;
        color: var(--text-muted);
        border-top: 1px solid var(--border);
        padding-top: var(--space-4);
        margin-top: var(--space-6);
        text-align: center;
    }
    .no-shadow-note {
        font-family: var(--font-mono);
        font-size: var(--text-sm);
        color: var(--text-muted);
        margin-top: var(--space-2);
    }

    /* ================================================================
       SESSION 1 -- Landing screen
       ================================================================ */

    .masthead-wordmark {
        font-family: var(--font-serif);
        font-weight: 700;
        font-size: var(--text-xl);
        color: var(--text-primary);
        letter-spacing: var(--tracking-tight);
        line-height: var(--leading-none);
    }
    /* SCAN READY pill -- decorative, not clickable */
    .scan-ready-pill {
        font-family: var(--font-mono);
        font-weight: 500;
        font-size: var(--text-xs);
        letter-spacing: var(--tracking-caps);
        color: var(--accent-amber);
        background-color: var(--accent-wash-4);
        border: none;
        border-radius: var(--radius-pill);
        padding: var(--space-1h) var(--space-3);
        cursor: default;
        user-select: none;
        pointer-events: none;
        line-height: var(--leading-none);
        display: inline-block;
    }

    /* Hero block */
    .hero {
        margin-top: var(--space-6); /* Added breathing room from the masthead */
        display: flex;
        flex-direction: column;
        justify-content: center;
        max-width: 460px;
        padding: 0; /* Stripped to prevent double-stacking */
    }
    .hero-headline {
        font-family: var(--font-serif);
        font-weight: 700;
        font-size: var(--text-3xl);
        color: var(--text-primary);
        line-height: var(--leading-tight);
        letter-spacing: var(--tracking-tighter);
        margin-bottom: var(--space-4);
    }
    .hero-subhead {
        font-family: var(--font-serif);
        font-weight: 400;
        font-size: var(--text-md);
        color: var(--text-muted);
        line-height: var(--leading-relaxed);
        margin-bottom: var(--space-4); /* Reduced from space-6 to pull CTA closer */
    }

    /* CTA button: override Streamlit default chrome (solid primary CTA) */
    .stButton > button,
    .stDownloadButton > button,
    .stFormSubmitButton > button {
        font-family: var(--font-mono) !important;
        font-weight: 500 !important;
        font-size: var(--button-font-size) !important;
        line-height: var(--leading-none) !important;
        letter-spacing: var(--tracking-widest) !important;
        color: var(--button-fg) !important;
        background-color: var(--button-bg) !important;
        border: none !important;
        border-radius: var(--button-radius) !important;
        padding: var(--space-3) var(--space-4) !important; /* even above and below: the label sits on the centre line */
        cursor: pointer !important;
        transition: opacity var(--duration-fast) ease !important;
        width: auto !important;
        white-space: nowrap !important;
        text-transform: uppercase !important; /* one case for every button, whatever case the label is stored in */
        text-align: center !important;
        justify-content: center !important;
        align-items: center !important;
        font-feature-settings: 'liga' 0, 'calt' 0 !important;
        font-variant-ligatures: none !important;
    }
    @media (hover: hover) {
        .stButton > button:hover,
        .stDownloadButton > button:hover,
        .stFormSubmitButton > button:hover {
            opacity: var(--button-hover-opacity) !important;
            background-color: var(--button-bg) !important;
            color: var(--button-fg) !important;
        }
    }
    .stButton > button:focus,
    .stButton > button:focus-visible,
    .stButton > button:active,
    .stDownloadButton > button:focus,
    .stDownloadButton > button:focus-visible,
    .stDownloadButton > button:active,
    .stFormSubmitButton > button:focus,
    .stFormSubmitButton > button:focus-visible,
    .stFormSubmitButton > button:active {
        box-shadow: none !important; /* keyboard focus is drawn by the shared :focus-visible ring */
    }

    /* Secondary button styling (outline/ghost) */
    button[kind="secondary"],
    .stButton > button[kind="secondary"],
    div.element-container:has(#cta-secondary-marker-ns) + div .stButton > button,
    div.element-container:has(#cta-secondary-marker) + div .stButton > button {
        background-color: transparent !important;
        color: var(--accent-amber) !important;
        border: 1px solid var(--accent-amber) !important;
    }
    @media (hover: hover) {
        button[kind="secondary"]:hover,
        .stButton > button[kind="secondary"]:hover,
        div.element-container:has(#cta-secondary-marker-ns) + div .stButton > button:hover,
        div.element-container:has(#cta-secondary-marker) + div .stButton > button:hover {
            background-color: var(--accent-wash-3) !important;
            color: var(--accent-amber) !important;
            border-color: var(--accent-amber) !important;
            opacity: 1 !important;
        }
    }
    button[kind="secondary"]:active,
    .stButton > button[kind="secondary"]:active,
    div.element-container:has(#cta-secondary-marker-ns) + div .stButton > button:active,
    div.element-container:has(#cta-secondary-marker) + div .stButton > button:active {
        background-color: transparent !important;
        opacity: 0.65 !important;
    }

    /* Landing footer -- kept in CSS for Session 0 foundation page; unused on landing */
    .landing-footer {
        font-family: var(--font-mono);
        font-weight: 400;
        font-size: var(--text-xs);
        letter-spacing: var(--tracking-wider);
        color: var(--text-muted);
        text-align: center;
        border-top: 1px solid var(--border);
        padding-top: var(--space-4);
        margin-top: var(--space-6);
    }

    /* ================================================================
       SESSION 1b -- Below-hero sections (Why / Process / Built-with / Closing CTA)
       ================================================================ */

    /* Shared section label (mono caps, small, muted) */
    .section-label {
        font-family: var(--font-mono);
        font-weight: 400;
        font-size: var(--text-xs);
        letter-spacing: var(--tracking-caps);
        text-transform: uppercase;
        color: var(--text-muted);
        margin-top: var(--space-2) !important; /* Ensures breathing room below dividers */
        margin-bottom: var(--space-3);
    }

    /* Section A -- Why this exists (stacked layout with optimal reading width) */
    .why-section {
        padding: var(--space-4) 0 0 0; /* Stripped bottom padding completely */
    }
    .why-body {
        font-family: var(--font-serif);
        font-weight: 400;
        font-size: var(--text-md);
        color: var(--text-muted);
        line-height: var(--leading-relaxed);
        margin: 0;
    }

    /* -- Security & Telemetry Bar -- */
    .security-bar {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: var(--space-5);
        padding: var(--space-5) 0;
        border-top: 1px solid var(--border);
        border-bottom: 1px solid var(--border);
        margin: var(--space-5) 0 var(--space-2) 0; /* Aggressively reduced bottom margin */
    }
    .why-section {
        margin-top: 0 !important;
    }

    /* -- Cinematic Entrance Animations -- */
    .typewriter-headline {
        /* Revealed left to right with a clip, so the text can wrap onto as many
           lines as the column needs. A width animation on a single unwrapped
           line cut the sentence off wherever the column ended. */
        white-space: normal;
        clip-path: inset(0 100% 0 0);
        animation: typeMainline 1.2s steps(45, end) 0.2s forwards;
    }
    @keyframes typeMainline {
        to { clip-path: inset(0 0 0 0); }
    }
    @media (max-width: 768px) {
        /* Mobile fallback so long headlines can wrap naturally */
        .typewriter-headline {
            white-space: normal;
            clip-path: none;
            animation: fadeSlideUp 0.8s ease-out forwards;
        }
    }

    .cascade-fade {
        opacity: 0;
        transform: translateY(15px);
        animation: fadeSlideUp 0.8s ease-out forwards;
    }
    @keyframes fadeSlideUp {
        to { opacity: 1; transform: translateY(0); }
    }

    /* Prevent Streamlit buttons from awkwardly floating before the cascade reaches them */
    div.element-container:has(#hero-cta-marker) + div,
    div.element-container:has(#footer-cta-marker) + div {
        opacity: 0;
        animation: fadeSlideUp 0.8s ease-out forwards;
    }
    div.element-container:has(#hero-cta-marker) + div { animation-delay: 1.3s; }
    div.element-container:has(#footer-cta-marker) + div { animation-delay: 2.5s; }
    .security-item h2 {
        font-family: var(--font-mono) !important;
        font-size: var(--text-xs);
        color: var(--accent-amber) !important;
        margin-bottom: var(--space-2);
        letter-spacing: var(--tracking-wide);
    }
    .security-item p {
        font-family: var(--font-mono);
        font-size: var(--text-xs);
        color: var(--text-muted);
        line-height: var(--leading-normal);
        margin: 0;
    }

    /* -- Rationale 2-Column Grid -- */
    .rationale-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: var(--space-5);
        margin-top: var(--space-4);
    }
    @media (max-width: 640px) { .rationale-grid { grid-template-columns: 1fr; } }
    .rationale-col h3 {
        font-family: var(--font-mono) !important;
        font-size: var(--text-sm);
        letter-spacing: var(--tracking-widest);
        color: var(--text-primary) !important;
        margin-bottom: var(--space-3);
        border-bottom: 1px solid var(--border);
        padding-bottom: var(--space-2);
    }

    /* -- Sleek Capabilities Grid -- */
    .caps-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: var(--space-6);
        margin: var(--space-6) 0 var(--space-5) 0;
    }
    @media (max-width: 640px) { .caps-grid { grid-template-columns: 1fr; } }
    .caps-item {
        background: transparent;
        padding: var(--space-4) 0 0 0;
        border-top: 1px solid var(--border);
    }
    .caps-item h4 {
        font-family: var(--font-serif) !important;
        font-size: var(--text-lg);
        color: var(--text-primary) !important;
        margin-bottom: var(--space-2);
        letter-spacing: var(--tracking-snug);
    }
    .caps-item p {
        font-family: var(--font-mono);
        font-size: var(--text-sm);
        color: var(--text-muted);
        line-height: var(--leading-relaxed);
        margin: 0;
    }

    /* Code-editor mockup in hero right column */
    .mock-editor {
        margin-top: var(--space-6); /* Matches the hero text margin */
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        font-family: var(--font-mono);
    }
    .mock-editor-bar {
        background-color: var(--surface-sunken);
        border-bottom: 1px solid var(--border);
        padding: var(--space-2h) var(--space-3);
        display: flex;
        align-items: center;
        gap: var(--space-1h);
    }
    .mock-editor-bar .dot {
        width: 10px; height: 10px;
        border-radius: 50%;
        display: inline-block;
    }
    .mock-editor-bar .filename {
        margin-left: auto;
        margin-right: auto;
        color: var(--text-muted);
        font-family: var(--font-mono);
        font-size: var(--text-xs);
    }
    .mock-editor-body {
        padding: var(--space-3) var(--space-4);
    }
    .mock-line {
        font-family: var(--font-mono);
        font-size: var(--text-sm);
        line-height: var(--leading-relaxed);
        display: flex;
        white-space: pre;
    }
    .mock-editor-status {
        border-top: 1px solid var(--border);
        padding: var(--space-2) var(--space-4);
        font-family: var(--font-mono);
        font-size: var(--text-xs);
        color: var(--accent-amber);
    }
    .mock-editor-lineno {
        display: inline-block;
        width: 1.8rem;
        color: var(--text-muted);
        user-select: none;
        flex-shrink: 0;
    }

    /* -- CSS Typewriter Animation -- */
    @keyframes typeLine {
        0% { max-width: 0; opacity: 1; }
        100% { max-width: 100%; opacity: 1; }
    }
    @keyframes blinkCursor {
        0%, 100% { border-right-color: transparent; }
        50% { border-right-color: var(--accent-amber); }
    }
    @keyframes statusSwap {
        0%, 70% { content: "> CodeT5 loaded, drafting"; color: var(--text-muted); }
        71%, 100% { content: "docstring drafted on this machine"; color: var(--color-success); }
    }

    .anim-typewriter {
        display: inline-block;
        overflow: hidden;
        white-space: nowrap;
        border-right: 2px solid var(--accent-amber);
        /* Waits for the 1.4s fade-in + a 0.6s dramatic pause = 2.0s delay */
        animation: typeLine 1.5s steps(40, end) 2.0s forwards, blinkCursor 0.5s step-end infinite;
        max-width: 0;
        vertical-align: bottom;
        color: var(--text-muted);
    }
    .anim-status::before {
        content: "> CodeT5 loaded, drafting";
        /* Extended the total time to 5.5s so the green success state triggers AFTER typing finishes */
        animation: statusSwap 5.5s forwards;
    }

    /* -- Timeline Hover Polish -- */
    .timeline-item {
        transition: background-color var(--duration-normal) ease, transform var(--duration-normal) ease;
        border-radius: var(--radius-md);
        padding: var(--space-4) !important;
    }
    @media (hover: hover) {
        .timeline-item:hover {
            background-color: var(--surface-raised); /* Subtle tactile hover */
        }
    }

    /* Sections B+C -- Unified Process + Built-With card */
    .process-card {
        background-color: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: var(--card-radius);
        padding: var(--space-5);
        margin-top: var(--space-5); /* Dramatically reduced from 72px calc */
    }
    /* Vertical timeline */
    .timeline {
        position: relative;
        padding-left: 2rem;
        margin-top: var(--space-4);
    }
    /* Draw line segment per-item, hiding on the final step */
    .timeline-item:not(:last-child)::after {
        content: '';
        position: absolute;
        left: calc(-1.55rem + 5.5px); /* Perfectly center behind the 12px bullet */
        top: 50%;
        height: 100%;
        width: 1px;
        background: var(--border);
        z-index: -1;
    }
    .timeline-item {
        position: relative;
        display: grid;
        grid-template-columns: 120px 1fr;
        gap: var(--space-5);
        align-items: center;
        padding: var(--space-4) 0; /* Increased from space-3 to give elements room to breathe */
    }
    .timeline-item::before {
        content: '';
        position: absolute;
        left: -1.55rem;
        top: 50%;
        transform: translateY(-50%);
        width: 12px;
        height: 12px;
        border-radius: 50%;
        border: 2px solid var(--accent-amber);
        background: var(--surface);
    }
    .timeline-left {
        display: flex;
        flex-direction: column;
        gap: var(--space-0h);
    }
    .timeline-index {
        font-family: var(--font-mono);
        font-weight: 500;
        font-size: var(--text-xs);
        color: var(--accent-amber);
        line-height: var(--leading-none);
    }
    .timeline-step {
        font-family: var(--font-mono);
        font-weight: 700;
        font-size: var(--text-xs);
        letter-spacing: var(--tracking-widest);
        text-transform: uppercase;
        color: var(--text-primary);
        line-height: var(--leading-none);
    }
    .timeline-desc {
        font-family: var(--font-serif);
        font-weight: 400;
        font-size: var(--text-base);
        color: var(--text-muted);
        line-height: var(--leading-normal);
        padding-top: 0;
    }
    /* Built-with inside card */
    .card-built-label {
        font-family: var(--font-mono);
        font-weight: 400;
        font-size: var(--text-xs);
        letter-spacing: var(--tracking-caps);
        text-transform: uppercase;
        color: var(--text-muted);
        margin-top: var(--space-4); /* Reduced from space-6 */
        padding-top: var(--space-4); /* Reduced from space-5 */
        border-top: 1px solid var(--border);
        margin-bottom: var(--space-3);
    }
    .built-tags {
        display: flex;
        flex-wrap: wrap;
        gap: var(--space-2);
    }
    .built-tag {
        font-family: var(--font-mono);
        font-weight: 400;
        font-size: var(--text-xs);
        letter-spacing: var(--tracking-wide);
        color: var(--text-strong) !important;
        border: 1px solid var(--border);
        border-radius: var(--radius-pill);
        padding: var(--space-1) var(--space-2h) !important;
        cursor: default;
        user-select: none;
        pointer-events: none;
        display: inline-block;
        line-height: var(--leading-none);
    }

    /* Remove Streamlit's injected gap above the footer */
    div.element-container:has(.closing-section) {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
    }

    /* Section D -- Closing CTA (tight, centered) */
    .closing-section {
        padding: var(--space-5) 0 0 0; /* Keep top padding, zero out bottom padding */
        text-align: center;
    }
    .closing-label {
        font-family: var(--font-serif) !important;
        font-weight: 400;
        font-size: var(--text-xl);
        color: var(--text-primary);
        margin-bottom: 0 !important; /* Strip the margin-bottom completely */
        text-transform: none;
        letter-spacing: normal;
    }

    /* Bulletproof centering and spacing for the closing CTA button */
    div:has(#footer-cta-marker) + div {
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
        margin-top: 0 !important; /* Zeroed out to prevent orphaned button */
    }
    div:has(#footer-cta-marker) + div > div,
    div:has(#footer-cta-marker) + div .stButton {
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
    }

    /* Secondary (outline) button -- Session 1b.
       DOM-verified structure (Streamlit 1.40 on Chrome/Blink):
       Each st.markdown / st.button renders into its own div.element-container
       child of the same div.stVerticalBlock.
       #cta-secondary lands inside one element-container;
       the st.button lands in the NEXT element-container sibling.
       Verified working selector: div:has(#cta-secondary) + div .stButton > button */
    /* Secondary (outline) button -- using new markers */
    div:has(#cta-secondary-marker) + div .stButton > button,
    div:has(#cta-secondary-marker-ask) + div .stButton > button,
    div:has(#cta-secondary-marker-ns) + div .stButton > button {
        background-color: transparent !important;
        color: var(--accent-amber) !important;
        border: 1px solid var(--accent-amber) !important;
    }
    @media (hover: hover) {
        div:has(#cta-secondary-marker) + div .stButton > button:hover,
        div:has(#cta-secondary-marker-ask) + div .stButton > button:hover,
        div:has(#cta-secondary-marker-ns) + div .stButton > button:hover {
            background-color: var(--accent-wash-3) !important;
            color: var(--accent-amber) !important;
            opacity: 1 !important;
        }
    }
    div:has(#cta-secondary-marker) + div .stButton > button:active,
    div:has(#cta-secondary-marker-ask) + div .stButton > button:active,
    div:has(#cta-secondary-marker-ns) + div .stButton > button:active {
        background-color: transparent !important;
        opacity: 0.65 !important;
    }

    /* Aggressively neutralize empty Streamlit containers holding our markers */
    div.element-container:has(#cta-secondary-marker),
    div.element-container:has(#cta-secondary-marker-ask),
    div.element-container:has(#cta-secondary-marker-ns),
    div.element-container:has(#cta-generate-marker),
    div.element-container:has(#docs-action-buttons) {
        display: none !important;
        margin-bottom: 0 !important;
        height: 0 !important;
        min-height: 0 !important;
        width: 0 !important;
    }

    /* ================================================================
       SESSION 2 -- Scan screen
       ================================================================ */

    /* -- Scan Screen UX Polish -- */
    .scan-parameters {
        font-family: var(--font-mono);
        font-weight: 400;
        font-size: var(--text-xs);
        color: var(--text-primary);
        letter-spacing: var(--tracking-wide);
        margin-top: -12px;
        margin-bottom: var(--space-5);
        background: var(--neutral-wash-1); /* Subtle dark tint */
        border-left: 2px solid var(--accent-amber);
        padding: var(--space-2) var(--space-2h);
        border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
    }

    div.element-container:has(.scan-microcopy) {
        margin-top: -12px !important;
        margin-bottom: var(--space-4) !important;
    }
    .scan-microcopy {
        font-family: var(--font-mono);
        font-size: var(--text-xs);
        color: var(--text-muted);
        background: var(--accent-wash-1); /* Amber tint */
        border: 1px solid var(--accent-line);
        padding: var(--space-2) var(--space-2h);
        border-radius: var(--radius-sm);
        display: flex;
        align-items: flex-start;
        gap: var(--space-2);
    }

    .scan-preview-row {
        display: flex;
        align-items: center;
        gap: var(--space-3);
        flex-wrap: wrap;
        margin-top: var(--space-2); /* GAP HALVED HERE */
        margin-bottom: var(--space-4);
    }
    .scan-preview-step {
        font-family: var(--font-mono);
        font-weight: 500;
        font-size: var(--text-xs);
        letter-spacing: var(--tracking-wide);
        color: var(--text-muted);
        background: transparent; /* Stripped heavy boxes */
        padding: 0;
        border: none;
    }
    .scan-preview-arrow {
        color: var(--border-strong);
        font-size: var(--text-sm);
    }

    div.element-container:has(.scan-security-tag) {
        margin-top: -8px !important;
    }
    .scan-security-tag {
        font-family: var(--font-mono);
        font-size: var(--text-xs);
        color: var(--text-muted);
        display: flex;
        align-items: center;
        gap: var(--space-2);
        background: var(--success-wash); /* Green tint */
        border: 1px solid var(--success-line);
        padding: var(--space-2) var(--space-2h);
        border-radius: var(--radius-sm);
    }

    .scan-input-section {
        padding: var(--space-5) 0 var(--space-4);
    }
    .scan-intro {
        font-family: var(--font-serif);
        font-weight: 400;
        font-size: var(--text-md);
        color: var(--text-muted);
        line-height: var(--leading-relaxed);
        margin: 0 0 var(--space-4) 0; /* Reduced from space-5 */
    }
    .scan-or-divider {
        display: flex;
        align-items: center;
        gap: var(--space-3);
        margin: var(--space-4) 0;
    }
    .scan-or-line {
        flex: 1;
        height: 1px;
        background: var(--border);
    }
    .scan-or-label {
        font-family: var(--font-mono);
        font-weight: 400;
        font-size: var(--text-xs);
        letter-spacing: var(--tracking-caps);
        color: var(--text-muted);
        flex-shrink: 0;
    }
    .scan-helper {
        font-family: var(--font-serif) !important;
        font-weight: 400;
        font-size: var(--text-md);
        line-height: var(--leading-relaxed);
        color: var(--text-muted);
        margin-top: 0 !important; /* Tuck tightly against the button */
    }
    .scan-error-line {
        font-family: var(--font-mono);
        font-weight: 400;
        font-size: var(--text-sm);
        color: var(--color-danger);
        margin-top: var(--space-3);
    }
    .scan-results-section {
        padding: 0 !important; /* Strip the 48px var(--space-6) top padding */
        margin-top: var(--space-4) !important; /* Reduced from 32px */
    }
    .scan-summary {
        font-family: var(--font-mono);
        font-weight: 400;
        font-size: var(--text-sm);
        color: var(--text-muted);
        margin-bottom: var(--space-5) !important;
    }
    /* Direct row hover with a visible opacity */
    .ledger-row {
        border-top: 1px solid var(--border);
        display: grid;
        grid-template-columns: 2.5rem 1fr auto;
        gap: var(--space-4);
        padding: var(--space-2h) var(--space-2h) !important; /* Tighter padding for vertical balance */
        align-items: center !important;
        margin: 0 !important;
        transition: background-color var(--duration-fast) ease;
    }

    @media (hover: hover) {
        .ledger-row:hover {
            background-color: var(--neutral-wash-2) !important;
            border-radius: var(--radius-sm);
            cursor: default;
        }
    }
    .ledger-row:last-child {
        border-bottom: 1px solid var(--border);
    }
    .ledger-index {
        font-family: var(--font-mono);
        font-weight: 500;
        font-size: var(--text-xs);
        color: var(--accent-amber);
        line-height: var(--leading-none);
    }
    .ledger-path {
        font-family: var(--font-mono);
        font-weight: 400;
        font-size: var(--text-sm);
        color: var(--text-primary);
        line-height: var(--leading-snug);
        overflow-wrap: anywhere;
    }
    .ledger-meta-missing {
        font-family: var(--font-mono);
        font-weight: 500;
        font-size: var(--text-xs);
        color: var(--accent-amber);
        line-height: var(--leading-none);
        white-space: nowrap;
        text-align: right;
    }
    .ledger-meta-clean {
        font-family: var(--font-mono);
        font-weight: 400;
        font-size: var(--text-xs);
        color: var(--text-muted);
        line-height: var(--leading-none);
        white-space: nowrap;
        text-align: right;
    }
    /* Tightly group the primary CTA with the estimate section */
    div:has(#cta-generate-marker) + div {
        margin-top: 0 !important; /* Rely entirely on Streamlit's neutralized natural gap */
    }
    .stFileUploader label,
    .stSelectbox label,
    .stTextInput label {
        font-family: var(--font-mono) !important;
        font-size: var(--text-xs) !important;
        font-weight: 400 !important;
        letter-spacing: var(--tracking-wider) !important;
        color: var(--text-muted) !important;
        text-transform: uppercase !important;
    }
    .stFileUploader > div {
        background-color: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-md) !important;
    }
    .stTextInput > div > div {
        background-color: var(--input-bg) !important;
        border: 1px solid var(--input-border) !important;
        border-radius: var(--input-radius) !important;
    }
    .stTextInput input {
        background-color: var(--input-bg) !important;
        color: var(--input-fg) !important;
        font-family: var(--font-mono) !important;
        font-size: var(--text-sm) !important;
        border: none !important;
        border-radius: var(--input-radius) !important;
    }
    /* Absolute override for Streamlit input placeholders */
    .stApp input::-webkit-input-placeholder {
        color: var(--input-placeholder) !important;
        opacity: 1 !important;
        -webkit-text-fill-color: var(--input-placeholder) !important;
    }
    .stApp input::-moz-placeholder {
        color: var(--input-placeholder) !important;
        opacity: 1 !important;
    }
    .stApp input::placeholder {
        color: var(--input-placeholder) !important;
        opacity: 1 !important;
    }
    /* Absolute override for Streamlit input wrappers & focus states */
    .stTextInput input:focus {
        outline: none !important;
        border: none !important;
        box-shadow: none !important;
    }
    div[data-baseweb="input"]:focus-within,
    .stTextInput > div > div:focus-within {
        border-color: var(--input-border-focus) !important;
        box-shadow: none !important;
    }

    /* Hide Streamlit form submission helper text */
    div[data-testid="InputInstructions"] {
        display: none !important;
    }

    /* Absolute override for Streamlit Expander content padding */
    div[data-testid="stExpanderDetails"],
    div[data-testid="stExpander"] details > div {
        padding-top: var(--space-4) !important;
    }

    /* -- Severity Pips (Scan Ledger) -- */
    .severity-pip {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: var(--space-2);
        vertical-align: middle;
        transform: translateY(-1px);
    }
    .pip-green { background-color: var(--color-success); }
    .pip-amber { background-color: var(--color-warning); }
    .pip-red { background-color: var(--color-danger); }

    .system-note {
        font-family: var(--font-mono);
        font-size: var(--text-xs);
        color: var(--text-muted);
        margin-top: var(--space-4);
        margin-bottom: var(--space-4);
        padding-top: var(--space-3);
        border-top: 1px dashed var(--border-subtle);
    }

    /* ================================================================
       SESSION 3 -- Generation / progress screen
       ================================================================ */

    /* -- Generation Telemetry Grid -- */
    .telemetry-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: var(--space-3);
        margin: var(--space-4) 0 var(--space-4) 0;
        border: 1px solid var(--card-border);
        border-radius: var(--card-radius);
        background: var(--card-bg);
        padding: var(--space-3) var(--space-4);
    }
    @media (max-width: 640px) {
        .telemetry-grid { grid-template-columns: 1fr; gap: var(--space-4); }
    }
    .telemetry-col {
        display: flex;
        flex-direction: column;
        gap: var(--space-1h);
    }
    .tel-label {
        font-family: var(--font-mono);
        font-size: var(--text-xs);
        letter-spacing: var(--tracking-caps);
        text-transform: uppercase;
        color: var(--text-muted);
    }
    .tel-value {
        font-family: var(--font-mono);
        font-weight: 500;
        font-size: var(--text-xs);
        color: var(--accent-amber);
    }

    /* Fraunces intro line (same treatment as .scan-intro / .why-body) */
    .gen-intro {
        font-family: var(--font-serif);
        font-weight: 400;
        font-size: var(--text-md);
        color: var(--text-muted);
        line-height: var(--leading-relaxed);
        margin: 0 0 var(--space-2) 0; /* Set to space-2 for perfect symmetry */
    }

    /* Outcome section wrapper */
    div.element-container:has(.gen-outcome-section) {
        margin-top: var(--space-4) !important; /* Increased breathing room from the terminal log */
    }
    .gen-outcome-section {
        padding: 0 !important;
        margin-top: 0 !important;
    }

    /* DOCUMENTATION READY label */
    .gen-outcome-label {
        font-family: var(--font-mono);
        font-weight: 400;
        font-size: var(--text-xs);
        letter-spacing: var(--tracking-caps);
        text-transform: uppercase;
        color: var(--text-muted);
        margin-bottom: var(--space-2);
    }

    /* Summary / file-count line */
    .gen-outcome-summary {
        font-family: var(--font-mono);
        font-weight: 400;
        font-size: var(--text-sm);
        color: var(--text-muted);
        margin-bottom: var(--space-3);
    }

    /* -- Generation Outcome Sub-summary -- */
    .gen-outcome-sub {
        font-family: var(--font-mono);
        font-size: var(--text-xs);
        color: var(--text-muted);
        margin-top: var(--space-2);
        line-height: var(--leading-normal);
    }

    /* Rate-limit error message */
    .gen-error-msg {
        font-family: var(--font-mono);
        font-weight: 400;
        font-size: var(--text-sm);
        color: var(--color-danger);
        margin-bottom: var(--space-3);
        line-height: var(--leading-normal);
    }

    /* Aggressively neutralize empty Streamlit containers for generation markers */
    div.element-container:has(#cta-view-docs-marker),
    div.element-container:has(#cta-try-again-marker) {
        margin-bottom: -1rem !important; /* Offset Streamlit's injected 1rem gap */
        height: 0 !important;
        min-height: 0 !important;
    }

    /* Generation CTA grouping */
    div:has(#cta-view-docs-marker) + div,
    div:has(#cta-try-again-marker) + div {
        margin-top: var(--space-3) !important; /* Reduced from 24px */
    }

    /* ================================================================
       SESSION 4 -- Documentation Viewer screen
       ================================================================ */

    /* Empty-state heading and subline */
    .docs-empty-head {
        font-family: var(--font-serif);
        font-weight: 700;
        font-size: var(--text-lg);
        color: var(--text-primary);
        margin: var(--space-6) 0 var(--space-3) 0;
    }
    .docs-empty-sub {
        font-family: var(--font-mono);
        font-weight: 400;
        font-size: var(--text-sm);
        color: var(--text-muted);
        margin-bottom: var(--space-5);
    }

    /* All-clean state message */
    .docs-all-clean {
        font-family: var(--font-mono);
        font-size: var(--text-sm);
        color: var(--text-muted);
        margin-top: var(--space-4); /* Added breathing room from preceding blocks */
        margin-bottom: var(--space-4);
    }

    /* File section header row */
    .docs-file-header {
        padding: var(--space-4) 0 var(--space-2) 0; /* Reduced padding */
        border: none !important;
        margin-top: 0 !important; /* Squashed */
    }

    /* Remove clean line borders */
    .docs-clean-line {
        font-family: var(--font-mono);
        font-weight: 400;
        font-size: var(--text-sm);
        color: var(--text-muted);
        padding: var(--space-2) 0; /* Reduced padding */
        border: none !important;
    }
    .docs-clean-line:last-of-type {
        border: none !important;
    }
    .docs-file-path {
        font-family: var(--font-mono);
        font-weight: 500;
        font-size: var(--text-sm);
        color: var(--accent-amber);
        letter-spacing: var(--tracking-wide);
        margin-bottom: var(--space-2);
    }

    /* Module overview paragraph */
    .docs-overview {
        font-family: var(--font-serif);
        font-weight: 400;
        font-size: var(--text-md);
        color: var(--text-muted);
        line-height: var(--leading-relaxed);
        margin: 0 0 var(--space-5) 0;
        overflow: hidden;
    }

    /* Fixed Drop Cap typography */
    .docs-overview.drop-cap::first-letter {
        font-family: var(--font-serif);
        font-weight: 700;
        font-size: 3.5em !important;
        line-height: 0.8 !important;
        margin-right: var(--space-2) !important;
        margin-top: var(--space-1) !important;
        float: left !important;
        color: var(--text-primary);
    }

    /* Remove function block dividers and embrace whitespace */
    .docs-fn-block {
        padding: 0 0 var(--space-3) 0 !important; /* Reduced padding */
        border: none !important;
        margin-bottom: var(--space-4) !important; /* Reduced margin */
    }
    .docs-fn-block:last-child {
        border-bottom: none !important;
        margin-bottom: var(--space-3) !important; /* Reduced margin */
    }

    /* Function name row: name + ai draft badge inline */
    .docs-fn-name-row {
        display: flex;
        align-items: center;
        gap: var(--space-2);
        margin-bottom: var(--space-3);
        flex-wrap: wrap;
    }
    .docs-fn-name {
        font-family: var(--font-mono);
        font-weight: 500;
        font-size: var(--text-sm);
        color: var(--text-primary);
        line-height: var(--leading-none);
    }

    .ai-draft-badge {
        font-family: var(--font-mono);
        font-weight: 500;
        font-size: var(--text-xs);
        letter-spacing: var(--tracking-widest);
        color: var(--accent-amber);
        border: 1px solid var(--accent-amber);
        border-radius: var(--radius-pill);
        padding: var(--space-0h) var(--space-2h) !important; /* Increased horizontal padding */
        cursor: default;
        user-select: none;
        pointer-events: none;
        line-height: var(--leading-none);
        display: inline-block;
        vertical-align: middle;
    }

    /* Two-column body: docstring (left) | source (right) */
    .docs-fn-cols {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: var(--space-4);
        align-items: start;
    }
    @media (max-width: 640px) {
        .docs-fn-cols {
            grid-template-columns: 1fr;
        }
    }

    /* Docstring column */
    .docs-docstring {
        font-family: var(--font-mono);
        font-weight: 400;
        font-size: var(--text-sm);
        color: var(--text-muted);
        line-height: var(--leading-relaxed);
    }

    /* Premium structured code blocks - Bypassing Streamlit's native pre styles */
    .docs-source-pre {
        background: var(--surface-code) !important;
        border: 1px solid var(--border-faint) !important;
        border-radius: var(--radius-base) !important;
        padding: var(--space-3) !important;
        margin: 0 !important;
        font-family: var(--font-mono) !important;
        font-size: var(--text-xs) !important;
        color: var(--text-muted) !important;
        line-height: var(--leading-relaxed) !important;
        white-space: pre-wrap !important;
        overflow-wrap: anywhere !important;
        overflow: hidden !important;
    }

    /* Divider before download button */
    .docs-footer-hairline {
        border: none;
        border-top: 1px solid var(--border);
        margin: var(--space-5) 0 var(--space-4) 0;
    }

    /* Download + back button wrapper */
    .docs-cta-wrap {
        padding: var(--space-2) 0;
        margin-top: var(--space-3) !important; /* Squeezed to prevent orphaned buttons */
    }

    /* -- Docs Screen Polish -- */
    .module-telemetry {
        font-family: var(--font-mono);
        font-size: var(--text-xs);
        color: var(--text-muted);
        letter-spacing: var(--tracking-wide);
        border-bottom: 1px solid var(--border);
        padding-bottom: var(--space-3);
        margin-bottom: var(--space-4);
        margin-top: -8px; /* Tucks it closer to the file path */
    }
    .docs-download-context {
        font-family: var(--font-mono);
        font-size: var(--text-xs);
        color: var(--text-muted);
        text-align: center;
        margin-bottom: var(--space-3);
    }

    /* ================================================================
       SESSION 5 -- Q&A screen
       ================================================================ */

    /* -- Q&A Screen Polish -- */
    .vector-status-bar {
        font-family: var(--font-mono);
        font-size: var(--text-xs);
        color: var(--text-muted);
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: var(--card-radius);
        padding: var(--space-2) var(--space-2h);
        margin-bottom: var(--space-4);
        display: inline-flex;
        align-items: center;
        gap: var(--space-2);
    }
    .vector-active-dot {
        color: var(--color-success);
        font-size: var(--text-sm);
        line-height: var(--leading-none);
    }
    .qa-disclaimer {
        font-family: var(--font-mono);
        font-size: var(--text-xs);
        color: var(--text-muted);
        text-align: center;
        margin-top: var(--space-2);
    }
    div.element-container:has(.qa-disclaimer) {
        margin-top: -1.2rem !important; /* Pulls disclaimer tightly under the input form */
    }

    /* Intro line (shown only when qa_chat_history is empty) */
    .qa-intro {
        font-family: var(--font-serif);
        font-weight: 400;
        font-size: var(--text-md);
        color: var(--text-muted);
        line-height: var(--leading-relaxed);
        margin: 0 0 var(--space-4) 0; /* Reduced from space-5 */
    }

    /* Example questions label */
    .qa-chips-label {
        font-family: var(--font-mono);
        font-weight: 400;
        font-size: var(--text-xs);
        letter-spacing: var(--tracking-caps);
        text-transform: uppercase;
        color: var(--text-muted);
        margin-bottom: var(--space-3);
    }

    /* Update chip button styles for native columns */
    div:has(.qa-chip-marker) + div .stButton > button {
        background-color: var(--surface) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-lg) !important;
        font-family: var(--font-serif) !important;
        font-weight: 400 !important;
        font-size: var(--text-sm) !important; /* Slightly smaller for a chip feel */
        padding: var(--space-2) var(--space-3) !important; /* Sleek vertical padding */
        width: 100% !important;
        height: auto !important; /* Let height shrink to fit */
        line-height: var(--leading-snug) !important;
        white-space: normal !important;
        text-transform: none !important; /* a suggested question reads as a sentence */
        text-align: left !important; /* Force text to the left */
        justify-content: flex-start !important; /* Force flex children to the left */
        transition: border-color var(--duration-fast) ease, background-color var(--duration-fast) ease !important;
    }
    @media (hover: hover) {
        div:has(.qa-chip-marker) + div .stButton > button:hover {
            border-color: var(--accent-amber) !important;
            background-color: var(--accent-wash-2) !important;
            color: var(--accent-amber) !important;
        }
    }

    /* Hide the markers */
    div.element-container:has(#qa-suggestions-container),
    div.element-container:has(.qa-chip-marker) {
        display: none !important;
        margin-bottom: 0 !important;
        height: 0 !important;
    }

    /* Transcript container */
    .qa-transcript {
        margin-bottom: var(--space-5);
    }

    /* Editorial turn with hairline divider */
    .qa-turn {
        border-top: 1px solid var(--border);
        padding: var(--space-4) 0;
    }
    .qa-turn:last-child {
        border-bottom: 1px solid var(--border);
        margin-bottom: var(--space-5);
    }

    /* Q row: amber mono "Q" label + Fraunces question */
    .qa-q-row {
        display: grid;
        grid-template-columns: 2rem 1fr;
        gap: var(--space-3);
        align-items: baseline;
        margin-bottom: var(--space-3);
    }

    /* A row: muted mono "A" label + Fraunces answer body */
    .qa-a-row {
        display: grid;
        grid-template-columns: 2rem 1fr;
        gap: var(--space-3);
        align-items: baseline;
    }

    .qa-turn-label {
        font-family: var(--font-mono);
        font-weight: 500;
        font-size: var(--text-sm);
        line-height: var(--leading-none);
    }
    .qa-q-label {
        color: var(--accent-amber);
    }
    .qa-a-label {
        color: var(--text-muted);
    }
    .qa-q-text {
        font-family: var(--font-serif);
        font-weight: 700;
        font-size: var(--text-lg);
        color: var(--text-primary);
        line-height: var(--leading-snug);
        letter-spacing: var(--tracking-snug);
    }
    .qa-a-body {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        gap: var(--space-2);
    }
    .qa-a-text {
        font-family: var(--font-serif);
        font-weight: 400;
        font-size: var(--text-md);
        color: var(--text-primary);
        line-height: var(--leading-relaxed);
    }
    .qa-a-fallback {
        color: var(--text-muted) !important;
    }

    /* Citation pill -- amber outline mono pill */
    .qa-citation-pill {
        font-family: var(--font-mono);
        font-weight: 500;
        font-size: var(--text-xs);
        letter-spacing: var(--tracking-wider);
        color: var(--accent-amber);
        border: 1px solid var(--accent-amber);
        border-radius: var(--radius-pill);
        padding: var(--space-1) var(--space-2h);
        cursor: default;
        user-select: none;
        pointer-events: none;
        line-height: var(--leading-none);
        display: inline-block;
        margin-top: var(--space-1);
    }

    /* Ask row container */
    div.element-container:has(.qa-ask-wrap) {
        margin-top: -1rem !important; /* Pull up to the suggestion chips */
    }
    .qa-ask-wrap {
        padding: 0 !important;
    }

    /* Streamlit Form border reset */
    .st-key-enterprise_sso_form {
        border: none !important;
        padding: 0 !important;
    }

    /* Q&A New Scan button container */
    div.element-container:has(.qa-new-scan-wrap) {
        margin-top: -1rem !important; /* Neutralize Streamlit's native gap */
    }
    .qa-new-scan-wrap {
        padding: 0 !important;
        margin-top: -1.5rem !important; /* Safely pull the button upward */
    }

    /* File uploader Browse files button styling override */
    .st-key-scan_file_upload button {
        background-color: transparent !important;
        color: var(--accent-amber) !important;
        border: 1px solid var(--accent-amber) !important;
        border-radius: var(--radius-md) !important;
        font-family: var(--font-mono) !important;
        font-weight: 500 !important;
        font-size: var(--button-font-size) !important;
        letter-spacing: var(--tracking-wider) !important;
        padding: var(--space-2) var(--space-4) !important;
        transition: background-color var(--duration-fast) ease, opacity var(--duration-fast) ease !important;
    }
    @media (hover: hover) {
        .st-key-scan_file_upload button:hover {
            background-color: var(--accent-wash-3) !important;
            color: var(--accent-amber) !important;
            opacity: 1 !important;
        }
    }

    /* ================================================================
       SESSION 6a -- Nav rail, Jump list, Estimates, Syntax highlighting
       ================================================================ */

    /* Expander styling in Scan screen */
    .stExpander {
        background-color: var(--card-bg) !important;
        border: 1px solid var(--card-border) !important;
        border-radius: var(--card-radius) !important;
        margin-top: var(--space-2) !important;
        margin-bottom: var(--space-4) !important;
    }
    .stExpander details {
        border: none !important;
    }
    .stExpander summary {
        font-family: var(--font-mono) !important;
        font-size: var(--text-xs) !important;
        font-weight: 500 !important;
        letter-spacing: var(--tracking-wider) !important;
        color: var(--text-muted) !important;
        /* No text-transform: titles contain function and class names, and
           get_domain_name is not GET_DOMAIN_NAME. Fixed labels are written in capitals. */
    }
    @media (hover: hover) {
        .stExpander summary:hover {
            color: var(--accent-amber) !important;
        }
    }

    /* Scan pre-flight estimate */
    .scan-estimate-section {
        margin-top: var(--space-4) !important; /* Reduced from 32px */
        margin-bottom: 0 !important;
    }
    .scan-estimate-body {
        font-family: var(--font-mono);
        font-weight: 400;
        font-size: var(--text-sm);
        color: var(--text-muted);
        margin: 0;
    }
    .scan-estimate-clean {
        font-family: var(--font-serif);
        font-weight: 400;
        font-size: var(--text-md);
        color: var(--text-muted);
        line-height: var(--leading-relaxed);
        margin: var(--space-4) 0 var(--space-2) 0;
    }

    div.element-container:has(.docs-jump-section) {
        margin-bottom: -1rem !important; /* Pull up the file headers below it */
    }
    /* Docs Jump list - Sleek Pill Redesign */
    .docs-jump-section {
        padding: var(--space-2) 0 var(--space-4) 0;
        border-top: none !important;
        margin-bottom: 0 !important;
    }
    /* Hide the redundant text label to clean up the UI */
    .docs-jump-section .section-label,
    .docs-jump-section p {
        display: none !important;
    }
    .docs-jump-links {
        display: flex;
        flex-wrap: wrap;
        gap: var(--space-2); /* Tighter gap for pills */
    }
    .docs-jump-link {
        font-family: var(--font-mono);
        font-weight: 400;
        font-size: var(--text-xs);
        color: var(--text-primary) !important;
        text-decoration: none !important; /* Remove underline */
        background-color: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-md); /* Pill shape */
        padding: var(--space-1h) var(--space-2h);
        transition: border-color var(--duration-fast) ease, color var(--duration-fast) ease, background-color var(--duration-fast) ease;
    }
    @media (hover: hover) {
        .docs-jump-link:hover {
            border-color: var(--accent-amber);
            color: var(--accent-amber) !important;
            background-color: var(--accent-wash-1);
        }
    }

    /* Syntax highlighting */
    .code-kw {
        color: var(--accent-amber);
        font-weight: 500;
    }
    .code-str {
        color: var(--text-muted);
    }


    /* ================================================================
       SESSION 7 -- Export screen
       ================================================================ */

    /* Export stats grid -- 3-column flex row */
    .export-stats-grid {
        display: flex;
        gap: var(--space-5);
        flex-wrap: wrap;
        margin: var(--space-4) 0 var(--space-5) 0;
        border-top: 1px solid var(--border);
        padding-top: var(--space-4);
    }
    .export-stat {
        display: flex;
        flex-direction: column;
        gap: var(--space-1);
        min-width: 120px;
    }
    .export-stat-value {
        font-family: var(--font-serif);
        font-weight: 700;
        font-size: var(--text-xl) !important; /* Reduced from 2rem */
        color: var(--accent-amber);
        letter-spacing: var(--tracking-tight);
        line-height: var(--leading-none);
    }
    .export-stat-label {
        font-family: var(--font-mono);
        font-weight: 400;
        font-size: var(--text-xs);
        letter-spacing: var(--tracking-caps);
        text-transform: uppercase;
        color: var(--text-muted);
    }
    .export-cta-wrap {
        padding: var(--space-2) 0 var(--space-6) 0;
        border-top: 1px solid var(--border);
    }

    /* ================================================================
       SESSION 7 -- Architecture screen
       ================================================================ */

    .arch-heading {
        font-family: var(--font-serif);
        font-weight: 600;
        font-size: var(--text-xl);
        color: var(--text-primary);
        line-height: var(--leading-snug);
        letter-spacing: var(--tracking-tight);
        margin: 0 0 var(--space-5) 0; /* Reduced from space-6 */
        max-width: 540px;
    }
    .arch-pipeline {
        border-top: 1px solid var(--border);
    }
    .arch-step {
        display: grid;
        grid-template-columns: 10rem 1fr;
        gap: var(--space-5);
        padding: var(--space-4) 0 !important; /* Reduced from 32px for tighter rows */
        border-bottom: 1px solid var(--border-subtle) !important;
        align-items: start !important; /* Prevent text shifting */
    }
    .arch-step-label {
        font-family: var(--font-mono);
        font-weight: 500;
        font-size: var(--text-xs);
        letter-spacing: var(--tracking-widest);
        text-transform: uppercase;
        color: var(--accent-amber);
        line-height: var(--leading-none);
        white-space: nowrap;
    }
    .arch-step-body {
        font-family: var(--font-serif);
        font-weight: 400;
        font-size: var(--text-base);
        color: var(--text-muted);
        line-height: var(--leading-relaxed);
        /* max-width removed to allow full horizontal span */
    }

    /* -- Architecture Screen Polish -- */
    .arch-io-tag {
        font-family: var(--font-mono);
        font-size: var(--text-xs);
        color: var(--accent-amber);
        margin-top: var(--space-3);
        letter-spacing: var(--tracking-wide);
        opacity: 0.85;
    }
    .arch-infra-telemetry {
        font-family: var(--font-mono);
        font-size: var(--text-xs);
        color: var(--text-muted);
        text-align: center;
        border-top: 1px dashed var(--border-subtle);
        padding-top: var(--space-4);
        margin-top: var(--space-6);
        margin-bottom: var(--space-4);
        letter-spacing: var(--tracking-wide);
        line-height: var(--leading-relaxed);
    }

    /* Ligature-off for new Session 7 mono classes */
    .export-stat-label,
    .arch-step-label,
    .archive-manifest,
    .session-disclaimer {
        font-feature-settings: 'liga' 0, 'calt' 0 !important;
        font-variant-ligatures: none !important;
    }

    /* -- Export Screen Polish -- */
    .archive-manifest {
        font-family: var(--font-mono);
        font-size: var(--text-sm);
        color: var(--text-muted);
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: var(--card-radius);
        padding: var(--space-4);
        margin-top: var(--space-4);
        margin-bottom: var(--space-5);
        line-height: var(--leading-relaxed);
        white-space: pre; /* Preserves the file tree spacing perfectly */
        overflow-x: auto;
    }
    .session-disclaimer {
        font-family: var(--font-mono);
        font-size: var(--text-xs);
        color: var(--text-muted);
        margin-top: var(--space-4);
        text-align: left;
    }
    /* -- File Uploader Sleek Redesign -- */
    .st-key-scan_file_upload section {
        background-color: var(--surface-sunken) !important;
        border: 1px dashed var(--border-strong) !important;
        border-radius: var(--radius-md) !important;
        padding: var(--space-4) !important;
        transition: border-color var(--duration-normal) ease, background-color var(--duration-normal) ease !important;
    }
    .st-key-scan_file_upload section:hover,
    .st-key-scan_file_upload section:focus-within {
        border-color: var(--accent-amber) !important;
        background-color: var(--accent-wash-1) !important;
    }
    /* Style the uploaded file list item background */
    .st-key-scan_file_upload [data-testid="stUploadedFile"] {
        background-color: var(--surface-sunken) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-md) !important;
    }
    /* Hide Streamlit's default giant cloud icon */
    .st-key-scan_file_upload section svg {
        display: none !important;
    }
    /* Restyle the small instruction text inside the dropzone */
    .st-key-scan_file_upload section small {
        font-family: var(--font-mono) !important;
        color: var(--text-muted) !important;
        font-size: var(--text-xs) !important;
        letter-spacing: var(--tracking-wide) !important;
    }

    /* ================================================================
       ACCESSIBILITY -- focus, disabled state, reduced motion
       ================================================================ */

    /* One visible keyboard-focus ring on every control. The :not(#_) pair raises
       specificity above the nav-rail and marker rules, which reset outlines.
       Text inputs are left out: their wrapper already turns amber on focus. */
    .stApp :is(button, a, summary, select, [role="button"], [role="tab"], [tabindex]:not([tabindex="-1"])):focus-visible:not(#_):not(#_) {
        outline: var(--focus-ring-width) solid var(--focus-ring-color) !important;
        outline-offset: var(--focus-ring-offset) !important;
    }

    /* A disabled button looks disabled and says so with the cursor. */
    .stApp button:disabled:not(#_),
    .stApp button[disabled]:not(#_) {
        opacity: var(--opacity-disabled) !important;
        cursor: not-allowed !important;
    }

    .stExpander summary {
        cursor: pointer !important;
    }

    /* People who ask their system for less motion get the final state at once. */
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-delay: 0s !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
            scroll-behavior: auto !important;
        }
        .typewriter-headline {
            clip-path: none !important;
        }
        .cascade-fade,
        div.element-container:has(#hero-cta-marker) + div,
        div.element-container:has(#footer-cta-marker) + div {
            opacity: 1 !important;
            transform: none !important;
        }
        .anim-typewriter {
            max-width: 100% !important;
            border-right-color: transparent !important;
        }
    }

    /* ================================================================
       INTERFACE REVIEW -- rules added from the rendered audit
       ================================================================ */

    /* Streamlit adds a 16px "link to heading" control to every heading. It is below
       the 24px target minimum and adds a tab stop per heading; the app has no use for it. */
    [data-testid="stHeaderActionElements"] {
        display: none !important;
    }

    /* Inline code and file names. Streamlit colours them green, which this app
       reserves for "documented / success". */
    [data-testid="stMarkdownContainer"] :not(pre) > code {
        color: var(--text-primary) !important;
        background-color: var(--surface-raised) !important;
    }

    /* Figures that sit in columns or change between runs keep one width per digit. */
    .export-stat-value,
    .ledger-index,
    .ledger-meta-missing,
    .ledger-meta-clean,

    /* Short headings break into even lines; paragraphs avoid a lone last word. */
    .hero-headline,
    .arch-heading,
    .closing-label,
    .qa-q-text {
        text-wrap: balance;
    }
    .hero-subhead,
    .why-body,
    .timeline-desc,
    .caps-item p,
    .arch-step-body,
    .qa-a-text {
        text-wrap: pretty;
    }

    /* The button that confirms a deletion uses the danger colour, not the brand accent. */
    div.element-container:has(.danger-marker) + div.element-container .stButton > button {
        background-color: var(--button-danger-bg) !important;
        color: var(--button-danger-fg) !important;
        border: none !important;
    }
    div.element-container:has(.danger-marker) {
        display: none !important;
    }

    /* iOS Safari zooms the page when a focused input is under 16px. */
    @media (max-width: 640px) {
        .stTextInput input {
            font-size: var(--text-base) !important;
        }
    }

    /* Streamlit 1.67 sets its own monospace (Source Code Pro) on these containers, and
       the page-level font rule above no longer reaches them. Without this, most of the
       text rendered in a second, near-identical monospace. Icons are left alone: they
       are ligatures in an icon font. Headings keep the serif through their own rule. */
    .stApp [data-testid="stMarkdownContainer"],
    .stApp [data-testid="stCaptionContainer"],
    .stApp [data-testid="stWidgetLabel"],
    .stApp [data-testid="stAlertContainer"],
    .stApp [data-testid="stExpander"] summary,
    .stApp .st-key-scan_file_upload section,
    .stApp [data-baseweb="select"],
    .stApp [data-baseweb="input"] input,
    .stApp [data-testid="stText"],
    .stApp code,
    .stApp pre {
        font-family: var(--font-mono) !important;
    }

    /* ================================================================
       P0 LAYER -- app shell, top bar, headings, button hierarchy.
       Later than every rule it overrides; keyed (.st-key-*) selectors only.
       ================================================================ */

    /* Streamlit's own header bar: the app draws its own. */
    header[data-testid="stHeader"] { display: none !important; }
    /* The scroll reset runs on screen changes only; its wrapper must not add a flex gap above the page. */
    .st-key-scroll_reset,
    [data-testid="stLayoutWrapper"]:has(> .st-key-scroll_reset) { display: none !important; }
    [data-testid="stMainBlockContainer"], .block-container {
        padding-top: var(--space-4) !important;
    }

    .rail-current, .rail-muted, .st-key-topbar_steps button p {
        font-family: var(--font-mono) !important;
        font-size: var(--text-sm) !important;
        line-height: var(--leading-none) !important;
        white-space: nowrap;
    }
    .rail-current {
        color: var(--text-primary);
        font-weight: 500;
        display: inline-block;
        padding: var(--space-1h) var(--space-2);
        border-radius: var(--radius-sm);
        background: var(--surface-raised);
        box-shadow: inset 0 -2px 0 var(--accent-amber) !important;
    }
    .rail-muted {
        color: var(--text-muted);
        opacity: var(--opacity-disabled);
        display: inline-block;
        padding: var(--space-1h) var(--space-2);
        cursor: default;
        user-select: none;
    }
    .rail-arrow {
        color: var(--border-strong);
        font-family: var(--font-mono);
        font-size: var(--text-sm);
        user-select: none;
    }
    .topbar-user {
        font-family: var(--font-mono);
        font-size: var(--text-sm);
        color: var(--text-muted);
        padding-right: var(--space-1);
    }

    /* Page headings: the screen name is the h1 */
    h1.page-h1, .stMarkdown h1.page-h1, h1.hero-headline {
        padding: 0 !important;
        scroll-margin-top: var(--space-6);
    }
    h1.hero-headline { margin: 0 0 var(--space-3) !important; }
    h1.page-h1, .stMarkdown h1.page-h1 {
        font-family: var(--font-serif) !important;
        font-size: var(--text-2xl) !important;
        font-weight: 700 !important;
        line-height: var(--leading-tight) !important;
        letter-spacing: var(--tracking-tight) !important;
        color: var(--text-primary) !important;
        margin: 0 0 var(--space-1) !important;
    }
    .page-sub {
        font-family: var(--font-serif);
        font-size: var(--text-md);
        color: var(--text-muted);
        line-height: var(--leading-normal);
        margin: 0 0 var(--space-2);
        max-width: 60ch;
    }
    .sr-only {
        position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px;
        overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; border: 0;
    }

    /* Sentence case everywhere: labels, eyebrows and stat captions keep the case they are written in. */
    .stApp [data-testid="stWidgetLabel"], .stApp [data-testid="stWidgetLabel"] p,
    .stFileUploader label, .stSelectbox label, .stTextInput label,
    .section-label, .export-stat-label, .arch-step-label, .gen-outcome-label,
    .tel-label, .qa-chips-label, .timeline-step {
        text-transform: none !important;
        letter-spacing: normal !important;
    }
    .stApp [data-testid="stWidgetLabel"] p { font-size: var(--text-sm) !important; color: var(--text-primary) !important; }
    h1.page-h1, .stMarkdown h1.page-h1 { margin-bottom: var(--space-3) !important; }
    h1.page-h1 + .page-sub { margin-top: calc(-1 * var(--space-2)) !important; }

    /* Buttons: sentence case, one size, one hierarchy -- primary fills, secondary outlines, tertiary is text. */
    :is(.stApp, [role="dialog"]) .stButton > button,
    :is(.stApp, [role="dialog"]) .stDownloadButton > button,
    :is(.stApp, [role="dialog"]) .stFormSubmitButton > button {
        text-transform: none !important;
        letter-spacing: normal !important;
        font-size: var(--text-sm) !important;
        font-weight: 500 !important;
        min-height: 2.5rem;
        padding: var(--space-2) var(--space-3) !important;
        border-radius: var(--radius-base) !important;
        transition: background-color var(--duration-fast) ease, border-color var(--duration-fast) ease,
                    color var(--duration-fast) ease, scale var(--duration-fast) ease-out !important;
    }
    :is(.stApp, [role="dialog"]) button[kind^="primary"] {
        background-color: var(--accent-amber) !important;
        color: var(--text-on-accent) !important;
        border: 1px solid var(--accent-amber) !important;
    }
    :is(.stApp, [role="dialog"]) button[kind^="secondary"] {
        background-color: transparent !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-strong) !important;
    }
    :is(.stApp, [role="dialog"]) button[kind^="tertiary"] {
        background-color: transparent !important;
        color: var(--text-muted) !important;
        border: 1px solid transparent !important;
        padding: var(--space-1h) var(--space-2) !important;
        min-height: 0;
    }
    :is(.stApp, [role="dialog"]) button[kind^="primary"] p, :is(.stApp, [role="dialog"]) button[kind^="secondary"] p, :is(.stApp, [role="dialog"]) button[kind^="tertiary"] p {
        color: inherit !important;
    }
    @media (hover: hover) {
        :is(.stApp, [role="dialog"]) button[kind^="primary"]:not(:disabled):hover {
            background-color: var(--color-amber-400) !important;
            opacity: 1 !important;
        }
        :is(.stApp, [role="dialog"]) button[kind^="secondary"]:not(:disabled):hover {
            border-color: var(--accent-amber) !important;
            color: var(--accent-amber) !important;
            background-color: var(--accent-wash-1) !important;
            opacity: 1 !important;
        }
        :is(.stApp, [role="dialog"]) button[kind^="tertiary"]:not(:disabled):hover {
            color: var(--text-primary) !important;
            background-color: var(--surface-raised) !important;
            opacity: 1 !important;
        }
    }
    @media (prefers-reduced-motion: no-preference) {
        :is(.stApp, [role="dialog"]) button:not(:disabled):active { scale: 0.96; }
    }
    /* Destructive confirmations: keys start with danger_ */
    :is(.stApp, [role="dialog"]) [class*="st-key-danger_"] button {
        background-color: var(--color-danger) !important;
        border-color: var(--color-danger) !important;
        color: var(--text-on-accent) !important;
    }

    /* Docs: the docstring reads as text, not code */
    .docs-docstring {
        font-family: var(--font-serif);
        font-size: var(--text-md);
        color: var(--text-primary);
        line-height: var(--leading-normal);
        margin: 0 0 var(--space-2);
    }

    /* Docs: rows sit on the container's own gap; names in rows read at body size */
    .stApp .stExpander { margin-top: 0 !important; margin-bottom: 0 !important; }
    .stExpander summary code { font-size: var(--text-sm) !important; background: transparent !important; padding: 0 !important; }
    .st-key-docs_overview h1, .st-key-docs_overview h2 {
        font-size: var(--text-lg) !important;
        padding: 0 0 var(--space-2) !important;
    }
    .st-key-docs_overview h3 { font-size: var(--text-md) !important; }
    #ghost-scan-estimate.scan-estimate-body { margin: var(--space-3) 0 var(--space-1) !important; }

    /* Scan: repo chip */
    .repo-chip {
        font-family: var(--font-mono);
        font-size: var(--text-sm);
        color: var(--text-primary);
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-pill);
        padding: var(--space-1h) var(--space-3);
        white-space: nowrap;
    }

    /* Audit log: room above the table for its hover toolbar, so it never covers the filters */
    [class*="st-key-audit_table"] { margin-top: var(--space-5) !important; }

    /* Landing hero */
    .hero { margin-top: 0 !important; max-width: 34rem; }
    .mock-editor { margin-top: 0 !important; }
    .mock-editor-body { overflow-x: auto; }
    .mock-line { display: block !important; white-space: pre !important; }
    .landing-h2 {
        font-family: var(--font-serif) !important;
        font-size: var(--text-xl) !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        padding: 0 !important;
        margin: 0 0 var(--space-3) !important;
    }
    .security-item h2 {
        font-family: var(--font-mono) !important;
        font-size: var(--text-sm) !important;
        font-weight: 500 !important;
        color: var(--accent-amber) !important;
        letter-spacing: normal !important;
        text-transform: none !important;
        padding: 0 !important;
        margin: 0 0 var(--space-1) !important;
    }
    .security-item p { font-size: var(--text-sm) !important; }
    ol.timeline, ol.arch-pipeline { list-style: none; margin: 0; padding-left: 2rem; }
    ol.arch-pipeline { padding-left: 0; }
    .timeline-item { grid-template-columns: 7rem 1fr !important; padding: var(--space-3) 0 !important; }
    .timeline-step { text-transform: none !important; letter-spacing: normal !important; font-size: var(--text-sm) !important; }
    .process-card .built-tags { margin-top: var(--space-4); padding-top: var(--space-4); border-top: 1px solid var(--border); }
    .arch-infra-item + .arch-infra-item::before { content: "\00B7"; padding: 0 var(--space-2); color: var(--border-strong); }
    .st-key-closing_cta { margin-top: var(--space-3); }


    /* ================================================================
       P1 LAYER -- stats, chat, docs list, generation steps, dialogs,
       code colours and interaction polish. Keyed selectors only.
       ================================================================ */

    /* Shared stat row */
    .stat-row {
        display: flex;
        flex-wrap: wrap;
        gap: var(--space-3) var(--space-6);
        margin: var(--space-1) 0 var(--space-4);
    }
    .stat { display: flex; flex-direction: column; gap: var(--space-1); min-width: 6rem; }
    .stat-value {
        font-family: var(--font-mono);
        font-size: var(--text-xl);
        font-weight: 500;
        line-height: var(--leading-none);
        color: var(--text-primary);
        font-variant-numeric: tabular-nums;
        white-space: nowrap;
    }
    .stat-label {
        font-family: var(--font-mono);
        font-size: var(--text-xs);
        color: var(--text-muted);
        line-height: var(--leading-snug);
    }
    .stat-note { margin-left: var(--space-1); color: var(--border-strong); }

    /* Dialogs */
    .dialog-body {
        font-family: var(--font-serif);
        font-size: var(--text-md);
        line-height: var(--leading-normal);
        color: var(--text-primary);
        margin: 0 0 var(--space-3);
    }
    div[role="dialog"] { border: 1px solid var(--border) !important; }

    /* Scan: one source card */
    .st-key-scan_source_card { margin-top: var(--space-1); }
    .stApp .st-key-scan_source_card:has(.scan-error-line) [data-testid="stTextInputRootElement"] {
        border-color: var(--color-danger) !important;
    }
    .scan-error-line {
        font-family: var(--font-mono);
        font-size: var(--text-sm) !important;
        color: var(--color-danger);
        margin: 0 !important;
    }
    /* The uploader repeats the size limit and type the caption already states. */
    .st-key-scan_file_upload [data-testid="stFileUploaderDropzoneInstructions"] { display: none !important; }
    .st-key-scan_stats { margin-bottom: var(--space-2); }
    .st-key-cta_generate_docs, .st-key-cta_scan_view_docs { margin-top: var(--space-2); }

    /* Generation steps */
    ol.gen-steps, .stMarkdown ol.gen-steps {
        list-style: none;
        padding-left: 0 !important;
        margin-left: 0 !important;
        display: flex;
        flex-wrap: wrap;
        gap: var(--space-2) var(--space-4);
        margin: 0 0 var(--space-2);
        padding: 0;
    }
    .gen-step {
        display: inline-flex;
        align-items: center;
        gap: var(--space-2);
        font-family: var(--font-mono);
        font-size: var(--text-sm);
        color: var(--text-muted);
        font-variant-numeric: tabular-nums;
    }
    .gen-step-marker {
        width: 1.5rem; height: 1.5rem;
        display: inline-flex; align-items: center; justify-content: center;
        border-radius: var(--radius-pill);
        border: 1px solid var(--border-strong);
        font-size: var(--text-xs);
    }
    .gen-step-done { color: var(--text-primary); }
    .gen-step-done .gen-step-marker { background: var(--accent-amber); border-color: var(--accent-amber); color: var(--text-on-accent); }
    .gen-step-current { color: var(--text-primary); font-weight: 500; }
    .gen-step-current .gen-step-marker { border-color: var(--accent-amber); color: var(--accent-amber); }
    .stProgress [role="progressbar"] div div { background-color: var(--accent-amber) !important; }

    /* Docs: file sections and definitions */
    .docs-file-head {
        display: flex;
        align-items: center;
        gap: var(--space-3);
        margin-bottom: var(--space-1);
    }
    h2.docs-file-name, .stMarkdown h2.docs-file-name {
        font-family: var(--font-mono) !important;
        font-size: var(--text-md) !important;
        font-weight: 500 !important;
        color: var(--text-primary) !important;
        padding: 0 !important;
        margin: 0 !important;
        letter-spacing: normal !important;
    }
    .docs-file-count {
        font-family: var(--font-mono);
        font-size: var(--text-xs);
        color: var(--text-muted);
        font-variant-numeric: tabular-nums;
        margin-left: auto;
        white-space: nowrap;
    }
    .docs-file-bar {
        width: 6rem; height: 4px;
        border-radius: var(--radius-pill);
        background: var(--surface-raised);
        overflow: hidden;
        display: inline-block;
    }
    .docs-file-bar span { display: block; height: 100%; background: var(--accent-amber); }
    [class*="st-key-docs_fn_"] {
        padding: var(--space-2h) 0;
        border-top: 1px solid var(--border-faint);
    }
    code.docs-sig {
        font-family: var(--font-mono) !important;
        font-size: var(--text-sm) !important;
        color: var(--text-strong) !important;
        background: transparent !important;
        padding: 0 !important;
    }
    .docs-docstring { margin: 0 !important; }
    .st-key-docs_filters { margin: var(--space-2) 0; }
    .st-key-docs_stats { margin-bottom: var(--space-1); }

    /* Q&A chat */
    .st-key-qa_meta { margin-bottom: var(--space-2); }
    .vector-status-bar {
        font-family: var(--font-mono);
        font-size: var(--text-xs);
        color: var(--text-muted);
        display: inline-flex; align-items: center; gap: var(--space-1h);
    }
    .vector-active-dot { color: var(--color-success); font-size: var(--text-xs); }
    [data-testid="stChatMessage"] {
        background: transparent !important;
        padding: var(--space-2) 0 !important;
        gap: var(--space-3) !important;
    }
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {
        font-family: var(--font-serif);
    }
    [data-testid="stChatMessageAvatarUser"], [data-testid="stChatMessageAvatarAssistant"],
    [data-testid="stChatMessageAvatarCustom"] {
        background: var(--surface-raised) !important;
        color: var(--accent-amber) !important;
        border: 1px solid var(--border);
    }
    .qa-citations { display: flex; flex-wrap: wrap; gap: var(--space-1h); margin-top: var(--space-1); }
    .qa-citations .qa-citation-pill {
        font-family: var(--font-mono);
        font-size: var(--text-xs);
        color: var(--accent-amber);
        border: 1px solid var(--border-strong);
        border-radius: var(--radius-pill);
        padding: var(--space-0h) var(--space-2h);
        background: var(--accent-wash-1);
    }
    .st-key-qa_chips { margin-top: var(--space-4); }
    [data-testid="stChatInput"] textarea { font-family: var(--font-mono) !important; }

    /* Code: warm palette instead of the default blue keywords */
    .stCode pre, .stCode code { color: var(--text-primary) !important; }
    .stCode .token.keyword, .stCode .token.builtin, .stCode .token.boolean { color: var(--accent-amber) !important; }
    .stCode .token.function, .stCode .token.class-name { color: var(--text-strong) !important; }
    .stCode .token.string, .stCode .token.triple-quoted-string { color: var(--color-success) !important; }
    .stCode .token.number { color: var(--color-amber-400) !important; }
    .stCode .token.comment { color: var(--text-muted) !important; font-style: italic; }
    .stCode .token.punctuation, .stCode .token.operator { color: var(--text-muted) !important; }
    .stCode .token.decorator, .stCode .token.annotation { color: var(--color-amber-400) !important; }

    /* Compact toggles (keys start with compact_): an inline disclosure, not a card */
    [class*="st-key-compact_"] .stExpander, .stExpander[class*="st-key-compact_"],
    [class*="st-key-compact_"] [data-testid="stExpander"] {
        background: transparent !important;
        border: none !important;
        margin: var(--space-1) 0 0 !important;
    }
    [class*="st-key-compact_"] summary {
        padding: var(--space-1) 0 !important;
        font-size: var(--text-xs) !important;
        color: var(--text-muted) !important;
    }
    [class*="st-key-compact_"] details { border: none !important; background: transparent !important; }

    /* P2: sticky, frosted top bar. The blur sits on a pseudo-element, not on the bar,
       so the command palette's fixed overlay is positioned against the viewport. */
    [data-testid="stLayoutWrapper"]:has(> .st-key-topbar_wrap) {
        position: sticky;
        top: 0;
        z-index: 999;
    }
    .st-key-topbar_wrap {
        position: relative;
        margin-bottom: var(--space-5);
        border-bottom: 1px solid var(--border);
    }
    .st-key-topbar_wrap::before {
        content: "";
        position: absolute;
        inset: calc(-1 * var(--space-4)) -100vw 0;
        background: var(--surface-frosted);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        z-index: -1;
    }
    .st-key-command_palette { position: absolute !important; width: 0; height: 0; }
    .section-h2, .stMarkdown h2.section-h2 {
        font-family: var(--font-serif) !important;
        font-size: var(--text-lg) !important;
        font-weight: 600 !important;
        padding: 0 !important;
        margin: var(--space-2) 0 0 !important;
    }

    /* Reruns keep content readable instead of greying it out */
    [data-stale="true"] { opacity: 1 !important; transition: none !important; }

    /* Hover and press: 150ms on the surfaces people interact with */
    [class*="st-key-docs_file_"], .st-key-scan_source_card, .ledger-row {
        transition: border-color var(--duration-fast) ease, background-color var(--duration-fast) ease;
    }
    @media (hover: hover) {
        [class*="st-key-docs_file_"]:hover, .st-key-scan_source_card:hover { border-color: var(--border-strong) !important; }
        .ledger-row:hover { background-color: var(--surface); }
        .stExpander summary:hover { color: var(--text-primary) !important; }
    }

    </style>
    """
    )
