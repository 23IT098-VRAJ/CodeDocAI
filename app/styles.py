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

        /* type families */
        --font-sans:   'Inter', system-ui, -apple-system, 'Segoe UI', sans-serif;
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
        --tracking-wide:    0.05em;
        --tracking-wider:   0.08em;
        --tracking-widest:  0.1em;

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
        --accent-wash-3:  rgba(var(--rgb-amber), 0.08);
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
        font-family:      var(--font-sans) !important;
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
        max-width: 1180px !important;
    }

    /* -- Global rule: zero box-shadow -- */
    *, *::before, *::after {
        box-shadow: none !important;
    }

    /* -- Prevent IBM Plex Mono ligature substitution -- */
    [style*="IBM Plex Mono"],
.type-label,
.swatch-name,
.spacing-label,
.r-label,
.page-subtitle,
.foundation-footer,
.no-shadow-note,
.built-tag,
.scan-error-line,
.ledger-index,
.ledger-path,
.ledger-meta,
.gen-error-msg,
.docs-docstring,
.docs-empty-head,
.docs-empty-sub,
.qa-citation-pill {
        font-feature-settings: 'liga' 0, 'calt' 0 !important;
        font-variant-ligatures: none !important;
    }

    /* -- Hide Streamlit chrome safely -- */
    footer {
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

    /* Hero block */
    .hero {
        margin-top: var(--space-6); /* Added breathing room from the masthead */
        display: flex;
        flex-direction: column;
        justify-content: center;
        max-width: 460px;
        padding: 0;    }
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
        margin-bottom: var(--space-4);    }

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
        box-shadow: none !important;    }

    /* Secondary button styling (outline/ghost) */
    button[kind="secondary"],
.stButton > button[kind="secondary"] {
        background-color: transparent !important;
        color: var(--accent-amber) !important;
        border: 1px solid var(--accent-amber) !important;
    }
    @media (hover: hover) {
        button[kind="secondary"]:hover,
.stButton > button[kind="secondary"]:hover {
            background-color: var(--accent-wash-3) !important;
            color: var(--accent-amber) !important;
            border-color: var(--accent-amber) !important;
            opacity: 1 !important;
        }
    }
    button[kind="secondary"]:active,
.stButton > button[kind="secondary"]:active {
        background-color: transparent !important;
        opacity: 0.65 !important;
    }

    /* -- Security & Telemetry Bar -- */
    .security-bar {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: var(--space-5);
        padding: var(--space-5) 0;
        border-top: 1px solid var(--border);
        border-bottom: 1px solid var(--border);
        margin: var(--space-5) 0 var(--space-2) 0;    }

    /* -- Cinematic Entrance Animations -- */
        @keyframes typeMainline {
        to { clip-path: inset(0 0 0 0); }
    }
    @media (max-width: 768px) {
            }

        @keyframes fadeSlideUp {
        to { opacity: 1; transform: translateY(0); }
    }

    /* Prevent Streamlit buttons from awkwardly floating before the cascade reaches them */
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

    /* -- Timeline Hover Polish -- */
    .timeline-item {
        transition: background-color var(--duration-normal) ease, transform var(--duration-normal) ease;
        border-radius: var(--radius-md);
        padding: var(--space-4) !important;
    }
    @media (hover: hover) {
        .timeline-item:hover {
            background-color: var(--surface-raised);        }
    }

    /* Sections B+C -- Unified Process + Built-With card */
    .process-card {
        background-color: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: var(--card-radius);
        padding: var(--space-5);
        margin-top: var(--space-5);    }
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
        padding: var(--space-4) 0;    }
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

    /* -- Scan Screen UX Polish -- */

                            .scan-error-line {
        font-family: var(--font-mono);
        font-weight: 400;
        font-size: var(--text-sm);
        color: var(--color-danger);
        margin-top: var(--space-3);
    }
    .scan-results-section {
        padding: 0 !important; /* Strip the 48px var(--space-6) top padding */
        margin-top: var(--space-4) !important;    }
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

    /* Rate-limit error message */
    .gen-error-msg {
        font-family: var(--font-mono);
        font-weight: 400;
        font-size: var(--text-sm);
        color: var(--color-danger);
        margin-bottom: var(--space-3);
        line-height: var(--leading-normal);
    }

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

    /* Docstring column */
    .docs-docstring {
        font-family: var(--font-mono);
        font-weight: 400;
        font-size: var(--text-sm);
        color: var(--text-muted);
        line-height: var(--leading-relaxed);
    }

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

    /* Streamlit Form border reset */

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
    }
    @media (hover: hover) {
        .stExpander summary:hover {
            color: var(--accent-amber) !important;
        }
    }

    /* Scan pre-flight estimate */
            .scan-estimate-clean {
        font-family: var(--font-serif);
        font-weight: 400;
        font-size: var(--text-md);
        color: var(--text-muted);
        line-height: var(--leading-relaxed);
        margin: var(--space-4) 0 var(--space-2) 0;
    }

    /* ================================================================
       SESSION 7 -- Architecture screen
       ================================================================ */

        .arch-pipeline {
        border-top: 1px solid var(--border);
    }
    .arch-step {
        display: grid;
        grid-template-columns: 10rem 1fr;
        gap: var(--space-5);
        padding: var(--space-4) 0 !important; /* Reduced from 32px for tighter rows */
        border-bottom: 1px solid var(--border-subtle) !important;
        align-items: start !important;    }
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
    .arch-step-label,
.archive-manifest {
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
                            }

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
    .ledger-index,
.ledger-meta-missing,
.ledger-meta-clean,
.hero-headline,
.closing-label {
        text-wrap: balance;
    }
    .hero-subhead,
.timeline-desc,
.arch-step-body {
        text-wrap: pretty;
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

    /* Streamlit's own header bar: the app draws its own. */
    header[data-testid="stHeader"] { display: none !important; }
    /* The scroll reset runs on screen changes only; its wrapper must not add a flex gap above the page. */
    .st-key-scroll_reset,
    [data-testid="stLayoutWrapper"]:has(> .st-key-scroll_reset) { display: none !important; }
    [data-testid="stMainBlockContainer"], .block-container {
        padding-top: var(--space-4) !important;
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
    .stApp [data-testid="stWidgetLabel"],
.stApp [data-testid="stWidgetLabel"] p,
.stFileUploader label,
.stSelectbox label,
.stTextInput label,
.arch-step-label,
.timeline-step {
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


    /* ================================================================
       FINAL LAYER -- type roles, skeletons.
       Inter carries interface text and prose; Fraunces the display headings;
       IBM Plex Mono only code, signatures, file paths and tabular figures.
       ================================================================ */
    /* Text elements only: spans and divs inherit, and Streamlit's icon spans keep their own font. */
    .stApp :is(p, li, label, button, input, textarea, select, summary, td, th) {
        font-family: var(--font-sans) !important;
    }
    .stApp :is(h1, h2, h3, h4, h5, h6):not(.docs-file-name):not(.security-item h2),
    .stApp :is(.hero-headline, .page-h1, .landing-h2, .section-h2, .closing-label) {
        font-family: var(--font-serif) !important;
    }
    .stApp :is(code, pre, kbd, samp, .docs-sig, .repo-chip, .ledger-path, .ledger-index, .ledger-meta-missing,
               .ledger-meta-clean, .docs-file-name, .docs-file-count, .stat-value, .archive-manifest,
               .vector-status-bar, .gen-step-marker, .swatch-name, .type-label, .spacing-label, .r-label),
    .stApp :is(pre, code) * {
        font-family: var(--font-mono) !important;
    }
    .stApp .security-item h2 { font-family: var(--font-sans) !important; font-weight: 600 !important; }
    .page-sub, .hero-subhead, .timeline-desc, .arch-step-body, .dialog-body,
    .stat-label, .timeline-step, .arch-step-label, .scan-error-line, .security-item p { font-family: var(--font-sans) !important; }

    .skeleton { display: flex; flex-direction: column; gap: var(--space-2h); padding: var(--space-2) 0; }
    .skeleton-bar {
        display: block;
        height: 0.75rem;
        border-radius: var(--radius-sm);
        background: var(--surface-raised);
    }
    @media (prefers-reduced-motion: no-preference) {
        .skeleton-bar {
            background: linear-gradient(90deg, var(--surface-raised) 0%, var(--border) 50%, var(--surface-raised) 100%);
            background-size: 200% 100%;
            animation: shimmer 1.2s ease-in-out infinite;
        }
    }
    @keyframes shimmer { from { background-position: 100% 0; } to { background-position: -100% 0; } }
</style>
    """
    )
