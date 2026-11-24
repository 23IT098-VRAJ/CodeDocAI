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
        --rgb-green:  76, 175, 80;

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
        --duration-reveal:  0.6s;

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
        --accent-glow:    rgba(var(--rgb-amber), 0.14);
        --accent-edge:    rgba(var(--rgb-amber), 0.45);
        --success-wash:   rgba(var(--rgb-green), 0.10);
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
        padding: 0;
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
        margin-bottom: var(--space-4);
    }

    /* CTA button: override Streamlit default chrome (solid primary CTA) */
    .stButton > button,
    .stDownloadButton > button,
    .stFormSubmitButton > button {
        font-family: var(--font-mono) !important;
        font-weight: 500 !important;
        font-size: var(--button-font-size) !important;
        line-height: var(--leading-none) !important;
        color: var(--button-fg) !important;
        background-color: var(--button-bg) !important;
        border: none !important;
        border-radius: var(--button-radius) !important;
        padding: var(--space-3) var(--space-4) !important; /* even above and below: the label sits on the centre line */
        cursor: pointer !important;
        transition: opacity var(--duration-fast) ease !important;
        width: auto !important;
        white-space: nowrap !important;
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
        box-shadow: none !important;
    }

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
        margin-top: var(--space-4) !important;
    }
    /* Direct row hover with a visible opacity */
    /* Scan results: ten rows (43.9 px each, measured), then the list scrolls on its own.
       No overscroll containment: at the list's end the wheel carries on down the page. */
    .scan-results-section {
        max-height: 27.5rem;
        overflow-y: auto;
        border-bottom: 1px solid var(--border);
        margin-bottom: var(--space-3);
    }
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
        color: var(--text-muted) !important;
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

    /* Ligature-off for the export manifest */
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
    .home-sub,
    .pipe-body,
    .zip-desc,
    .faq p {
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
    .stTextInput label {
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
    [role="dialog"] { border: 1px solid var(--border) !important; }

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
        inset: calc(-1 * var(--space-4)) calc(-1 * var(--space-3)) 0;
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

    /* Text elements only: spans and divs inherit, and Streamlit's icon spans keep their own font. */
    .stApp :is(p, li, label, button, input, textarea, select, summary, td, th) {
        font-family: var(--font-sans) !important;
    }
    .stApp :is(h1, h2, h3, h4, h5, h6):not(.docs-file-name),
    .stApp :is(.hero-headline, .page-h1, .landing-h2, .section-h2, .closing-label) {
        font-family: var(--font-serif) !important;
    }
    .stApp :is(code, pre, kbd, samp, .docs-sig, .repo-chip, .ledger-path, .ledger-index, .ledger-meta-missing,
    .ledger-meta-clean, .docs-file-name, .docs-file-count, .stat-value, .archive-manifest,
    .vector-status-bar, .gen-step-marker, .swatch-name, .type-label, .spacing-label, .r-label),
    .stApp :is(pre, code) * {
        font-family: var(--font-mono) !important;
    }
    .page-sub, .hero-subhead, .dialog-body, .stat-label, .scan-error-line { font-family: var(--font-sans) !important; }

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


    /* ================================================================
       HOME PAGE SECTIONS -- below the hero. Each section fades up as it
       scrolls into view (.home-reveal and the keyed containers, see the
       effects script); motion inside a section starts from .revealed.
       ================================================================ */
    .home-section { margin-top: var(--space-6); scroll-margin-top: 6rem; }
    .stApp .home-kicker {
        font-family: var(--font-mono) !important;
        font-size: var(--text-xs);
        letter-spacing: var(--tracking-wider);
        text-transform: uppercase;
        color: var(--accent-amber);
        margin: 0 0 var(--space-2);
    }
    .stApp .landing-h2.home-title { font-size: var(--text-2xl) !important; line-height: var(--leading-tight); margin: 0 0 var(--space-2) !important; scroll-margin-top: 6rem; }
    .home-sub {
        font-size: var(--text-base);
        line-height: var(--leading-normal);
        color: var(--text-muted);
        max-width: 40rem;
        margin: 0 0 var(--space-4);
    }
    .home-note {
        font-family: var(--font-mono);
        font-size: var(--text-xs);
        letter-spacing: var(--tracking-wide);
        color: var(--text-muted);
        margin: var(--space-3) 0 0;
    }
    .home-card {
        position: relative;
        background-color: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: var(--card-radius);
        padding: var(--space-4);
    }
    .home-icon { width: 1.25rem; height: 1.25rem; display: block; }

    /* Measured figures */
    .home-stats {
        margin-top: var(--space-6);
        padding: var(--space-4) 0;
        border-top: 1px solid var(--border);
        border-bottom: 1px solid var(--border);
    }
    .home-stats .stat-row { margin: 0; justify-content: space-between; }
    .home-stats .stat-value { font-size: var(--text-2xl); color: var(--accent-amber); }

    /* Try it */
    .st-key-tryit { margin-top: var(--space-6); scroll-margin-top: 6rem; }
    .st-key-tryit textarea {
        font-family: var(--font-mono) !important;
        font-size: var(--text-sm) !important;
        line-height: var(--leading-relaxed) !important;
        background: var(--surface) !important;
        white-space: pre !important;
        overflow-x: auto !important;
    }
    .code-pane {
        margin: 0;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        overflow: hidden;
    }
    .code-pane figcaption {
        display: flex;
        align-items: center;
        gap: var(--space-2h);
        padding: var(--space-2) var(--space-3);
        background: var(--surface-sunken);
        border-bottom: 1px solid var(--border-subtle);
        font-family: var(--font-mono);
        font-size: var(--text-xs);
    }
    .pane-tab {
        color: var(--text-primary);
        padding: var(--space-0h) var(--space-2h);
        border-radius: var(--radius-sm);
        background: var(--surface-raised);
        box-shadow: inset 0 -2px 0 var(--accent-amber);
    }
    .pane-note { margin-left: auto; color: var(--text-muted); }
    .try-out.has-result .pane-note { color: var(--color-success); }
    .stApp .pane-code {
        margin: 0;
        padding: var(--space-2h) 0;
        background: transparent;
        border: 0;
        font-size: var(--text-xs);
        line-height: var(--leading-relaxed);
        color: var(--text-primary);
        overflow-x: auto;
        white-space: pre;
    }
    .try-out { min-height: 22rem; display: flex; flex-direction: column; }
    .try-empty {
        margin: auto;
        padding: var(--space-5);
        text-align: center;
        font-size: var(--text-sm);
        color: var(--text-muted);
    }
    .try-error { color: var(--color-danger); }
    .try-meta {
        display: block;
        margin-top: var(--space-2);
        font-family: var(--font-mono);
        font-size: var(--text-xs);
        color: var(--color-success);
    }
    .ln { display: block; padding-right: var(--space-3); }
    .ln-no {
        display: inline-block;
        width: 3ch;
        margin-right: var(--space-3);
        text-align: right;
        color: var(--border-strong);
        user-select: none;
    }
    .ln-add { background: var(--success-wash); box-shadow: inset 2px 0 0 var(--color-success); }
    .ln-add, .ln-add .tk-string { color: var(--color-success); }
    .tk-keyword { color: var(--accent-amber); }
    .tk-builtin, .tk-number, .tk-decorator { color: var(--color-amber-400); }
    .tk-name { color: var(--text-strong); font-weight: 500; }
    .tk-string { color: var(--color-success); }
    .tk-comment { color: var(--text-muted); font-style: italic; }

    /* How it works: the heading here, the tour is a component below it */
    .home-section.how { margin-bottom: 0; }
    .st-key-how_tour { margin-top: calc(-1 * var(--space-2)); }

    /* What you get */
    .get-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(14rem, 1fr)); gap: var(--space-3); }
    .get-card { display: flex; flex-direction: column; gap: var(--space-2); transition: transform var(--duration-normal) ease, border-color var(--duration-normal) ease; }
    .get-icon {
        width: 2.5rem;
        height: 2.5rem;
        display: grid;
        place-items: center;
        border-radius: var(--radius-base);
        color: var(--accent-amber);
        background: var(--accent-wash-3);
        border: 1px solid var(--accent-edge);
        margin-bottom: var(--space-1);
    }
    .get-icon::before { content: ""; width: 1.25rem; height: 1.25rem; background: currentColor; -webkit-mask: center / contain no-repeat; mask: center / contain no-repeat; }
    .get-icon-folder::before { -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.75' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z'/%3E%3C/svg%3E"); mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.75' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z'/%3E%3C/svg%3E"); }
    .get-icon-diff::before { -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.75' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M12 3v8M8 7h8M8 17h8'/%3E%3Crect x='3' y='3' width='18' height='18' rx='2'/%3E%3C/svg%3E"); mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.75' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M12 3v8M8 7h8M8 17h8'/%3E%3Crect x='3' y='3' width='18' height='18' rx='2'/%3E%3C/svg%3E"); }
    .get-icon-chart::before { -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.75' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M4 20V10M10 20V4M16 20v-7M22 20H2'/%3E%3C/svg%3E"); mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.75' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M4 20V10M10 20V4M16 20v-7M22 20H2'/%3E%3C/svg%3E"); }
    .get-icon-doc::before { -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.75' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z'/%3E%3Cpath d='M14 3v5h5M9 13h6M9 17h4'/%3E%3C/svg%3E"); mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='1.75' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z'/%3E%3Cpath d='M14 3v5h5M9 13h6M9 17h4'/%3E%3C/svg%3E"); }
    .stApp .home-card h3.get-name {
        font-family: var(--font-mono) !important;
        font-size: var(--text-sm) !important;
        font-weight: 500 !important;
        color: var(--text-primary) !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    .get-desc { font-size: var(--text-sm); line-height: var(--leading-normal); color: var(--text-muted); margin: 0; }
    .get-badge {
        margin-top: auto;
        align-self: flex-start;
        font-family: var(--font-mono);
        font-size: var(--text-xs);
        color: var(--color-success);
        border: 1px solid var(--color-success);
        border-radius: var(--radius-pill);
        padding: var(--space-0h) var(--space-2h);
    }
    @media (hover: hover) { .get-card:hover { transform: translateY(-3px); } }

    /* What a third-party AI gets to see: repository -> server -> cloud */
    .flowmap {
        display: grid;
        grid-template-columns: 9rem 3rem minmax(0, 1fr) 9rem minmax(0, 1fr);
        align-items: center;
    }
    .node-label { display: block; font-size: var(--text-sm); font-weight: 600; color: var(--text-primary); margin-bottom: var(--space-2); }
    .node-sub { display: block; font-family: var(--font-mono); font-size: var(--text-xs); color: var(--text-muted); }
    .node-repo {
        border: 1px dashed var(--border-strong);
        border-radius: var(--card-radius);
        padding: var(--space-3);
        text-align: center;
    }
    .node-repo .node-label { margin-bottom: var(--space-1); }
    .node-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: var(--space-2); }
    .node-list li { font-size: var(--text-sm); line-height: var(--leading-snug); color: var(--text-muted); padding-left: var(--space-3); border-left: 2px solid var(--color-success); }
    .node-list-cloud li { border-left-color: var(--accent-amber); display: flex; flex-direction: column; gap: var(--space-0h); }
    .priv-item { font-weight: 600; color: var(--text-primary); }
    .pipe-link { position: relative; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: var(--space-2); padding: 0 var(--space-1); }
    .pipe-link span {
        display: block;
        width: 100%;
        height: 2px;
        background: repeating-linear-gradient(90deg, var(--border-strong) 0 6px, transparent 6px 12px);
    }
    .pipe-link-gate span { background: repeating-linear-gradient(90deg, var(--accent-amber) 0 6px, transparent 6px 12px); }
    .pipe-link em {
        order: -1;
        font-style: normal;
        font-family: var(--font-mono);
        font-size: var(--text-xs);
        white-space: nowrap;
        color: var(--accent-amber);
        border: 1px solid var(--accent-edge);
        border-radius: var(--radius-pill);
        padding: var(--space-0h) var(--space-2);
        background: var(--accent-wash-1);
    }

    /* Before you scan */
    .faq-section { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.7fr); gap: var(--space-6); align-items: start; }
    .faq-list { border-top: 1px solid var(--border); }
    .faq { border-bottom: 1px solid var(--border); interpolate-size: allow-keywords; }
    .faq::details-content {
        block-size: 0;
        overflow: hidden;
        transition: block-size var(--duration-normal) ease, content-visibility var(--duration-normal) allow-discrete;
    }
    .faq[open]::details-content { block-size: auto; }
    .faq summary {
        list-style: none;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: var(--space-3);
        padding: var(--space-3) 0;
        font-size: var(--text-base);
        font-weight: 500;
        color: var(--text-primary);
        transition: color var(--duration-fast) ease;
    }
    .faq summary::-webkit-details-marker { display: none; }
    .faq summary::after {
        content: "+";
        flex: none;
        width: 1.75rem;
        height: 1.75rem;
        display: grid;
        place-items: center;
        border: 1px solid var(--border-strong);
        border-radius: var(--radius-pill);
        font-family: var(--font-mono);
        color: var(--accent-amber);
        transition: transform var(--duration-normal) ease, border-color var(--duration-normal) ease;
    }
    .faq[open] summary::after { transform: rotate(45deg); border-color: var(--accent-amber); }
    .faq[open] summary { color: var(--accent-amber); }
    .faq p { margin: 0 0 var(--space-3); padding-right: var(--space-6); font-size: var(--text-sm); line-height: var(--leading-normal); color: var(--text-muted); }
    @media (hover: hover) { .faq summary:hover { color: var(--accent-amber); } }

    @media (max-width: 640px) {
        .home-stats .stat-row { justify-content: flex-start; }
        .faq-section, .flowmap { grid-template-columns: minmax(0, 1fr); gap: var(--space-3); }
        .pipe-link { flex-direction: row; min-height: var(--space-5); }
        .pipe-link span { width: 2px; height: var(--space-5); background: repeating-linear-gradient(180deg, var(--border-strong) 0 6px, transparent 6px 12px); }
        .pipe-link-gate span { background: repeating-linear-gradient(180deg, var(--accent-amber) 0 6px, transparent 6px 12px); }
        .pipe-link em { order: 1; }
        .faq p { padding-right: 0; }
    }

    /* Motion inside the sections, from the moment each is revealed. Without it
       (reduced motion, or no script) everything shows in its finished state. */
    @media (prefers-reduced-motion: no-preference) {
        .takeaways.revealed .get-card { animation: rise-in 500ms cubic-bezier(0.2, 0, 0, 1) both; animation-delay: var(--reveal-delay); }
        .takeaways.revealed .get-card:nth-child(2) { animation-delay: calc(var(--reveal-delay) + 100ms); }
        .takeaways.revealed .get-card:nth-child(3) { animation-delay: calc(var(--reveal-delay) + 200ms); }
        .takeaways.revealed .get-card:nth-child(4) { animation-delay: calc(var(--reveal-delay) + 300ms); }
        .privacy.revealed .flowmap > * { animation: rise-in 500ms cubic-bezier(0.2, 0, 0, 1) both; }
        .privacy.revealed .flowmap > :nth-child(2) { animation-delay: calc(var(--reveal-delay) + 150ms); }
        .privacy.revealed .flowmap > :nth-child(3) { animation-delay: calc(var(--reveal-delay) + 300ms); }
        .privacy.revealed .flowmap > :nth-child(4) { animation-delay: calc(var(--reveal-delay) + 450ms); }
        .privacy.revealed .flowmap > :nth-child(5) { animation-delay: calc(var(--reveal-delay) + 600ms); }
        .privacy.revealed .pipe-link span { animation: dash-flow 800ms linear 5; animation-delay: calc(var(--reveal-delay) + 700ms); }
        .try-out.has-result .ln-add { animation: line-in 520ms cubic-bezier(0.2, 0, 0, 1) both; animation-delay: calc(var(--a) * 160ms); }
    }
    @keyframes dash-flow { from { background-position: 0 0; } to { background-position: 24px 0; } }
    @keyframes line-in { from { opacity: 0; transform: translateX(-8px); } to { opacity: 1; transform: none; } }

    /* ================================================================
       DOCUMENTATION READY -- what the run produced
       ================================================================ */
    .st-key-gen_done_actions { margin-bottom: var(--space-5); }
    .done-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(22rem, 1fr)); gap: var(--space-3); }
    .done-card {
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: var(--card-radius);
        padding: var(--space-4);
    }
    .done-wide { margin-top: var(--space-3); }
    .stApp h2.done-h, .stApp h2.qa-side-h {
        font-family: var(--font-mono) !important;
        font-size: var(--text-xs) !important;
        font-weight: 500 !important;
        letter-spacing: var(--tracking-wider) !important;
        text-transform: uppercase;
        color: var(--accent-amber) !important;
        padding: 0 !important;
        margin: 0 0 var(--space-3) !important;
    }
    .done-legend { display: flex; align-items: center; gap: var(--space-2); margin: 0 0 var(--space-3); font-size: var(--text-xs); color: var(--text-muted); }
    .done-legend i { display: inline-block; width: var(--space-2h); height: var(--space-1h); border-radius: var(--radius-pill); }
    .done-legend i + i { margin-left: var(--space-2); }
    .stApp :is(ul.cov-list, ul.found-list, ul.long-list) { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: var(--space-2h); }
    .cov-row { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.2fr) auto; gap: var(--space-3); align-items: center; }
    .cov-path { font-family: var(--font-mono); font-size: var(--text-xs); color: var(--text-primary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .cov-bar { position: relative; height: var(--space-2); border-radius: var(--radius-pill); background: var(--surface-raised); overflow: hidden; }
    .cov-bar i { position: absolute; left: 0; top: 0; bottom: 0; border-radius: var(--radius-pill); }
    .cov-bar .after, .done-legend .after { background: var(--accent-amber); }
    .cov-bar .before, .done-legend .before { background: var(--border-strong); }
    .split-bar { display: flex; height: var(--space-2h); border-radius: var(--radius-pill); overflow: hidden; background: var(--surface-raised); margin-bottom: var(--space-3); }
    .split-bar i { display: block; height: 100%; }
    .split-bar .before { background: var(--border-strong); }
    .split-bar .drafted, .done-legend .drafted { background: var(--accent-amber); }
    .split-bar .missing, .done-legend .missing { background: var(--color-danger); }
    .done-legend { flex-wrap: wrap; }
    .found-list li { display: flex; align-items: baseline; gap: var(--space-2); font-size: var(--text-sm); color: var(--text-muted); }
    .found-list b { min-width: 3.5rem; font-family: var(--font-mono); font-weight: 500; color: var(--text-primary); font-variant-numeric: tabular-nums; }
    .long-row { display: grid; grid-template-columns: minmax(0, 1.2fr) minmax(0, 1fr) minmax(0, 1.4fr) 5.5rem; gap: var(--space-3); align-items: center; }
    .long-name { font-family: var(--font-mono); font-size: var(--text-sm); color: var(--text-primary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .long-file { font-family: var(--font-mono); font-size: var(--text-xs); color: var(--text-muted); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .long-bar { height: var(--space-1h); border-radius: var(--radius-pill); background: var(--surface-raised); overflow: hidden; }
    .long-bar i { display: block; height: 100%; border-radius: inherit; background: var(--accent-amber); }
    .long-loc { font-family: var(--font-mono); font-size: var(--text-xs); color: var(--text-muted); text-align: right; font-variant-numeric: tabular-nums; }
    .cov-num { font-family: var(--font-mono); font-size: var(--text-xs); color: var(--text-muted); font-variant-numeric: tabular-nums; white-space: nowrap; }
    .done-note { margin: var(--space-3) 0 0; font-size: var(--text-xs); color: var(--text-muted); }
    @media (prefers-reduced-motion: no-preference) {
        .cov-bar i, .split-bar i, .long-bar i { animation: grow-x 700ms cubic-bezier(0.2, 0, 0, 1) both; transform-origin: left; }
        .cov-bar .after { animation-delay: 250ms; }
        .done-card { animation: rise-in 450ms cubic-bezier(0.2, 0, 0, 1) both; }
        .done-grid .done-card:nth-child(2) { animation-delay: 100ms; }
        .done-wide { animation-delay: 200ms; }
    }
    @keyframes grow-x { from { transform: scaleX(0); } to { transform: scaleX(1); } }

    /* ================================================================
       DOCS -- the overview's headings stand apart from its text
       ================================================================ */
    .stApp .st-key-docs_overview h2 {
        font-family: var(--font-serif) !important;
        font-size: var(--text-xl) !important;
        color: var(--text-strong) !important;
        padding: 0 0 var(--space-2h) !important;
        margin: 0 0 var(--space-3) !important;
        border-bottom: 1px solid var(--border);
    }
    .stApp .st-key-docs_overview h3 {
        font-family: var(--font-mono) !important;
        font-size: var(--text-xs) !important;
        font-weight: 500 !important;
        letter-spacing: var(--tracking-wider) !important;
        text-transform: uppercase;
        color: var(--accent-amber) !important;
        padding: 0 !important;
        margin: var(--space-5) 0 var(--space-2) !important;
    }
    .st-key-docs_overview li::marker { color: var(--accent-amber); }

    /* ================================================================
       Q&A -- the empty page: questions to start with, and what answers use
       ================================================================ */
    .st-key-qa_empty { margin-top: var(--space-4); }
    .stApp [class*="st-key-qa_chip_"] .stButton,
    .stApp [class*="st-key-qa_chip_"] button[kind="secondary"] { width: 100% !important; }
    .stApp [class*="st-key-qa_chip_"] button[kind="secondary"] {
        min-height: 4rem !important;
        justify-content: flex-start !important;
        text-align: left !important;
        padding: var(--space-2h) var(--space-3) !important;
        border-color: var(--border) !important;
        background-color: var(--surface) !important;
        color: var(--text-primary) !important;
    }
    @media (hover: hover) {
        .stApp [class*="st-key-qa_chip_"] button[kind="secondary"]:hover {
            border-color: var(--accent-amber) !important;
            background-color: var(--accent-wash-3) !important;
        }
    }
    .stApp [class*="st-key-qa_chip_"] button > div { justify-content: flex-start !important; width: 100%; }
    .stApp [class*="st-key-qa_chip_"] button p {
        font-size: var(--text-sm) !important;
        line-height: var(--leading-snug) !important;
        white-space: normal !important;
        overflow-wrap: break-word;
        text-wrap: balance;
        text-align: left;
    }
    .stApp ol.how-strip {
        list-style: none;
        margin: 0;
        padding: 0;
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: var(--space-3);
    }
    .how-step {
        position: relative;
        display: grid;
        grid-template-columns: auto minmax(0, 1fr);
        align-content: start;
        column-gap: var(--space-2h);
        row-gap: var(--space-1);
        padding: var(--space-3) var(--space-4);
        border: 1px solid var(--border);
        border-radius: var(--card-radius);
        background: var(--surface);
    }
    .how-num {
        grid-row: span 2;
        width: 1.75rem;
        height: 1.75rem;
        display: grid;
        place-items: center;
        border-radius: var(--radius-pill);
        font-family: var(--font-mono);
        font-size: var(--text-xs);
        color: var(--text-on-accent);
        background: var(--accent-amber);
    }
    .how-name { font-size: var(--text-sm); font-weight: 600; color: var(--text-primary); }
    .how-text { font-size: var(--text-sm); line-height: var(--leading-normal); color: var(--text-muted); }
    .qa-hint { margin-bottom: var(--space-5) !important; }
    @media (max-width: 640px) { .stApp ol.how-strip { grid-template-columns: minmax(0, 1fr); } }
    .qa-hint { margin: var(--space-3) 0 0; font-size: var(--text-sm); color: var(--text-muted); }

    /* ================================================================
       MOTION -- one orchestrated entrance on the landing page, quiet
       feedback everywhere else. Nothing moves under reduced motion.
       ================================================================ */
    .hero-word { display: inline-block; white-space: nowrap; }
    .hero-caret { display: none; }
    .st-key-hero_window { position: relative; }
    .st-key-hero_window::before {
        content: "";
        position: absolute;
        inset: -12% -10%;
        background: radial-gradient(closest-side, var(--accent-wash-3), transparent);
        filter: blur(24px);
        z-index: -1;
        pointer-events: none;
    }
    [class*="st-key-docs_file_"], .home-card { position: relative; }
    @media (hover: hover) {
        [class*="st-key-docs_file_"]::after, .home-card::after {
            content: "";
            position: absolute;
            inset: 0;
            border-radius: inherit;
            pointer-events: none;
            opacity: 0;
            transition: opacity var(--duration-normal) ease;
            background: radial-gradient(360px circle at var(--spot-x, 50%) var(--spot-y, 50%), var(--accent-glow), transparent 60%);
        }
        [class*="st-key-docs_file_"]:hover::after, .home-card:hover::after { opacity: 1; }
        [class*="st-key-docs_file_"]:hover, .home-card:hover { border-color: var(--accent-edge) !important; }
    }
    .gen-steps .gen-step + .gen-step::before {
        content: "";
        width: var(--space-4);
        height: 2px;
        margin-right: var(--space-2);
        border-radius: var(--radius-pill);
        background: var(--border);
    }
    .gen-steps .gen-step-done + .gen-step::before { background: var(--accent-amber); }
    .gen-check { width: 0.75rem; height: 0.75rem; }
    .gen-check path { stroke-dasharray: 16; stroke-dashoffset: 0; }

    @media (prefers-reduced-motion: no-preference) {
        /* Typed headline: 62 characters at 22 ms each, done by about 1.5 s. */
        .hero-char {
            animation: char-in 20ms steps(1, start) both, caret-pass 44ms steps(1, end);
            animation-delay: calc(150ms + var(--c) * 22ms);
        }
        .hero-caret {
            display: inline-block;
            width: 0.06em;
            height: 0.85em;
            margin-left: 0.04em;
            vertical-align: baseline;
            background: var(--accent-amber);
            animation: caret-life 1700ms linear 1480ms both;
        }
        .st-key-hero_window {
            animation: window-in 450ms cubic-bezier(0.2, 0, 0, 1) 1600ms both;
        }
        .gen-step-latest .gen-check path { animation: draw-check 360ms ease-out both; }
        .gen-steps .gen-step-latest::before { animation: fill-line 360ms ease-out both; transform-origin: left; }
        [role="dialog"] { animation: dialog-in 180ms cubic-bezier(0.2, 0, 0, 1) both; }

    }
    @keyframes char-in { from { opacity: 0; } to { opacity: 1; } }
    @keyframes caret-pass { from { box-shadow: 0.06em 0 0 var(--accent-amber); } to { box-shadow: none; } }
    /* Hidden before typing ends, blinks twice, then goes. */
    @keyframes caret-life { 0% { opacity: 0; } 1%, 25% { opacity: 1; } 26%, 50% { opacity: 0; } 51%, 75% { opacity: 1; } 76%, 100% { opacity: 0; } }
    @keyframes window-in { from { opacity: 0; transform: translateY(12px) scale(0.98); } to { opacity: 1; transform: none; } }
    @keyframes rise-in { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: none; } }
    @keyframes draw-check { from { stroke-dashoffset: 16; } to { stroke-dashoffset: 0; } }
    @keyframes fill-line { from { transform: scaleX(0); } to { transform: scaleX(1); } }
    @keyframes dialog-in { from { opacity: 0; transform: translateY(8px) scale(0.97); } to { opacity: 1; transform: none; } }
    .st-key-fx_scripts, [data-testid="stLayoutWrapper"]:has(> .st-key-fx_scripts) { display: none !important; }

    /* Hero order: headline types (0.15-1.5 s), editor fades in (1.6 s) and types (2.1-3.1 s), then the text below. */
    @media (prefers-reduced-motion: no-preference) {
        .hero-after { animation: rise-in 500ms cubic-bezier(0.2, 0, 0, 1) 3150ms both; }
        .st-key-hero_cta { animation: rise-in 500ms cubic-bezier(0.2, 0, 0, 1) 3300ms both; }
        .fx-reveal :is(.home-reveal, .st-key-tryit, .st-key-how_tour, .closing-section, .st-key-closing_cta) {
            --reveal-delay: 0s;
        }
        .fx-reveal :is(.home-reveal, .st-key-tryit, .st-key-how_tour, .closing-section, .st-key-closing_cta):not(.revealed) {
            opacity: 0;
            transform: translateY(16px);
        }
        .fx-reveal :is(.home-reveal, .st-key-tryit, .st-key-how_tour, .closing-section, .st-key-closing_cta).revealed {
            transition: opacity var(--duration-reveal) cubic-bezier(0.2, 0, 0, 1) var(--reveal-delay),
                        transform var(--duration-reveal) cubic-bezier(0.2, 0, 0, 1) var(--reveal-delay);
        }
    }

    /* Index loader on the Generate screen (index_loader.py). The ring's fill (--ixl-p) is
       registered as a percentage by the effects script (helpers._FX_SCRIPT), so it can animate
       from the last batch's value (--from) to this one (--to). An @property rule would
       need angle brackets here, which make the sanitizer drop the whole stylesheet. */
    .ixl {
        min-height: 52vh;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: var(--space-3);
        text-align: center;
    }
    .ixl-ring {
        --ixl-p: var(--to);
        position: relative;
        width: 148px;
        height: 148px;
        border-radius: var(--radius-pill);
        background: conic-gradient(var(--accent-amber) var(--ixl-p), var(--surface-raised) 0);
        display: grid;
        place-items: center;
    }
    .ixl-ring::before {
        content: "";
        position: absolute;
        inset: 12px;
        border-radius: inherit;
        background: var(--bg);
    }
    .ixl-pct {
        position: relative;
        font-family: var(--font-mono);
        font-size: var(--text-2xl);
        font-weight: 500;
        color: var(--text-primary);
        font-variant-numeric: tabular-nums;
    }
    .ixl-pct small { font-size: var(--text-base); color: var(--accent-amber); margin-left: var(--space-0h); }
    .ixl-orbit { position: absolute; inset: -14px; border-radius: inherit; }
    .ixl-orbit i {
        position: absolute;
        top: 0;
        left: 50%;
        width: 8px;
        height: 8px;
        margin-left: -4px;
        border-radius: var(--radius-pill);
        background: var(--accent-amber);
    }
    .ixl-orbit i:nth-child(2) { background: var(--color-success); transform-origin: 4px 88px; rotate: 120deg; }
    .ixl-orbit i:nth-child(3) { background: var(--text-primary); transform-origin: 4px 88px; rotate: 240deg; }
    .stApp .ixl-title {
        font-family: var(--font-serif) !important;
        font-size: var(--text-2xl) !important;
        font-weight: 700;
        color: var(--text-primary);
        margin: var(--space-2) 0 0;
    }
    .stApp .ixl-chip {
        font-family: var(--font-mono) !important;
        font-size: var(--text-sm);
        color: var(--accent-amber);
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-pill);
        padding: var(--space-1) var(--space-3);
        margin: 0;
        font-variant-numeric: tabular-nums;
    }
    .ixl-lines { position: relative; height: 1.5em; width: min(36rem, 90vw); margin: 0; color: var(--text-muted); }
    .ixl-lines span { position: absolute; inset: 0; visibility: hidden; }
    .ixl-lines span:first-child { visibility: visible; }
    @media (prefers-reduced-motion: no-preference) {
        .ixl-ring { animation: ixl-fill 700ms cubic-bezier(0.2, 0, 0, 1) both; }
        /* the orbit and the lines resume where the last redraw left them (--t is negative) */
        .ixl-orbit { animation: ixl-spin 2400ms linear infinite; animation-delay: var(--t); }
        .ixl-orbit i { animation: ixl-bob 1200ms ease-in-out infinite alternate; animation-delay: var(--t); }
        .ixl-lines span { visibility: visible; animation: ovl-cycle 12000ms linear infinite backwards; }
        .ixl-lines span:nth-child(1) { animation-delay: var(--t); }
        .ixl-lines span:nth-child(2) { animation-delay: calc(var(--t) + 3000ms); }
        .ixl-lines span:nth-child(3) { animation-delay: calc(var(--t) + 6000ms); }
        .ixl-lines span:nth-child(4) { animation-delay: calc(var(--t) + 9000ms); }
    }
    @keyframes ixl-fill { from { --ixl-p: var(--from); } to { --ixl-p: var(--to); } }
    @keyframes ixl-spin { to { transform: rotate(360deg); } }
    @keyframes ixl-bob { from { opacity: 0.45; } to { opacity: 1; } }

    /* Overview loader on the Generate screen: the CodeT5 loading screen's pattern,
       its own mark (a page writing itself). One loop is 3.6 s; see overview_loader.py. */
    .ovl {
        min-height: 52vh;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: var(--space-3);
        text-align: center;
    }
    .ovl-mark {
        width: 64px;
        height: 80px;
        padding: 18px 14px;
        border-radius: var(--radius-base);
        border: 2px solid var(--accent-amber);
        background: var(--accent-wash-3);
        display: flex;
        flex-direction: column;
        gap: 9px;
    }
    .ovl-line { display: block; height: 6px; border-radius: var(--radius-pill); background: var(--accent-amber); transform-origin: left; }
    .ovl-line:nth-child(2) { width: 80%; }
    .ovl-line:nth-child(3) { width: 60%; }
    .stApp .ovl-title {
        font-family: var(--font-serif) !important;
        font-size: var(--text-2xl) !important;
        font-weight: 700;
        color: var(--text-primary);
        margin: var(--space-2) 0 0;
    }
    .stApp .ovl-chip {
        font-family: var(--font-mono) !important;
        font-size: var(--text-sm);
        color: var(--accent-amber);
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-pill);
        padding: var(--space-1) var(--space-3);
        margin: 0;
    }
    .ovl-lines { position: relative; height: 1.5em; width: min(36rem, 90vw); margin: 0; color: var(--text-muted); }
    .ovl-lines span { position: absolute; inset: 0; visibility: hidden; }
    .ovl-lines span:first-child { visibility: visible; }
    .ovl-bar { width: min(18rem, 70vw); height: 4px; border-radius: var(--radius-pill); background: var(--surface-raised); overflow: hidden; }
    .ovl-bar span { display: block; width: 100%; height: 100%; border-radius: inherit; background: var(--accent-amber); transform-origin: left; }
    .ovl-note { font-size: var(--text-xs); color: var(--text-muted); margin: 0; }
    @media (prefers-reduced-motion: no-preference) {
        .ovl-line { animation: ovl-write-1 3600ms linear infinite; }
        .ovl-line:nth-child(2) { animation-name: ovl-write-2; }
        .ovl-line:nth-child(3) { animation-name: ovl-write-3; }
        .ovl-bar span { animation: ovl-fill 3600ms linear infinite; }
        .ovl-lines span { visibility: visible; animation: ovl-cycle 14400ms linear infinite backwards; }
        .ovl-lines span:nth-child(2) { animation-delay: 3600ms; }
        .ovl-lines span:nth-child(3) { animation-delay: 7200ms; }
        .ovl-lines span:nth-child(4) { animation-delay: 10800ms; }
    }
    /* each mark line writes in its own slice of the loop, then holds until the loop ends */
    @keyframes ovl-write-1 { 0%, 8% { transform: scaleX(0); } 28%, 100% { transform: scaleX(1); } }
    @keyframes ovl-write-2 { 0%, 30% { transform: scaleX(0); } 50%, 100% { transform: scaleX(1); } }
    @keyframes ovl-write-3 { 0%, 52% { transform: scaleX(0); } 72%, 100% { transform: scaleX(1); } }
    @keyframes ovl-fill { 0% { transform: scaleX(0); } 83%, 100% { transform: scaleX(1); } }
    /* one line per loop: it fades in as its loop starts and out as the next one starts */
    @keyframes ovl-cycle {
        0% { opacity: 0; transform: translateY(6px); }
        1.5%, 25% { opacity: 1; transform: none; }
        26.5%, 100% { opacity: 0; transform: translateY(-6px); }
    }

    /* Loading screen while CodeT5 warms up */
    .boot {
        min-height: 70vh;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: var(--space-3);
        text-align: center;
    }
    .boot-mark {
        display: flex;
        align-items: flex-end;
        gap: 10px;
        height: 64px;
        padding: 14px 18px;
        border-radius: var(--radius-lg);
        background: var(--accent-amber);
    }
    .boot-quote { width: 10px; height: 36px; border-radius: var(--radius-pill); background: var(--surface); }
    .stApp .boot-title {
        font-family: var(--font-serif) !important;
        font-size: var(--text-2xl) !important;
        font-weight: 700;
        color: var(--text-primary);
        margin: var(--space-2) 0 0;
    }
    .stApp .boot-code {
        font-family: var(--font-mono) !important;
        font-size: var(--text-sm);
        color: var(--text-primary);
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-base);
        padding: var(--space-2) var(--space-3);
        margin: 0;
        white-space: nowrap;
    }
    .boot-kw { color: var(--accent-amber); }
    .boot-doc {
        display: inline-block;
        vertical-align: bottom;
        overflow: hidden;
        color: var(--color-success);
        border-right: 2px solid var(--accent-amber);
    }
    .boot-lines { position: relative; height: 1.5em; width: min(36rem, 90vw); margin: 0; color: var(--text-muted); }
    .boot-lines span { position: absolute; inset: 0; opacity: 0; }
    .boot-lines span:first-child { opacity: 1; }
    .boot-bar { width: min(18rem, 70vw); height: 4px; border-radius: var(--radius-pill); background: var(--surface-raised); overflow: hidden; }
    .boot-bar span { display: block; width: 40%; height: 100%; border-radius: inherit; background: var(--accent-amber); }
    .boot-note { font-size: var(--text-xs); color: var(--text-muted); margin: 0; }
    @media (prefers-reduced-motion: no-preference) {
        .boot-quote { animation: quote-bounce 900ms cubic-bezier(0.2, 0, 0, 1) infinite alternate; }
        .boot-quote:nth-child(2) { animation-delay: 150ms; }
        .boot-quote:nth-child(3) { animation-delay: 300ms; }
        .boot-lines span { animation: line-cycle 10s infinite; }
        .boot-lines span:first-child { opacity: 0; }
        .boot-lines span:nth-child(2) { animation-delay: 2.5s; }
        .boot-lines span:nth-child(3) { animation-delay: 5s; }
        .boot-lines span:nth-child(4) { animation-delay: 7.5s; }
        .boot-bar span { animation: bar-slide 1.4s ease-in-out infinite; }
        .boot-doc { animation: type-loop 3.2s steps(36, end) infinite, caret 0.8s step-end infinite; }
    }
    @keyframes quote-bounce { from { height: 14px; } to { height: 36px; } }
    @keyframes line-cycle {
        0% { opacity: 0; transform: translateY(6px); }
        4%, 22% { opacity: 1; transform: none; }
        26%, 100% { opacity: 0; transform: translateY(-6px); }
    }
    @keyframes type-loop { 0% { max-width: 0; } 55%, 85% { max-width: 36ch; } 100% { max-width: 0; } }
    @keyframes caret { 50% { border-right-color: transparent; } }
    @keyframes bar-slide { from { transform: translateX(-110%); } to { transform: translateX(260%); } }

    /* Q&A meta line: one row, centred with New scan */
    .st-key-qa_meta { margin-bottom: 0; }
    .st-key-qa_meta p { margin: 0 !important; }
    .st-key-scan_status [data-testid="stExpanderDetails"] {
        max-height: 26.5rem;  /* ten status lines (about 2.6rem each) */
        overflow-y: auto;
        overscroll-behavior: contain;
    }
    .stApp :is(.st-key-qa_new_scan_bottom, .st-key-docs_ask_top) button[kind="secondary"] {
        border-color: var(--accent-amber) !important;
        color: var(--accent-amber) !important;
        background-color: var(--accent-wash-3) !important;
    }
    .stApp :is(.st-key-qa_new_scan_bottom, .st-key-docs_ask_top) button[kind="secondary"] p { color: var(--accent-amber) !important; font-weight: 600; }
    @media (hover: hover) {
        .stApp :is(.st-key-qa_new_scan_bottom, .st-key-docs_ask_top) button[kind="secondary"]:hover { background-color: var(--accent-glow) !important; }
    }
    .qa-meta-note { font-size: var(--text-xs); color: var(--text-muted); margin-left: var(--space-3); }
    .st-key-qa_chips { margin-top: var(--space-2) !important; }
</style>
    """
    )
