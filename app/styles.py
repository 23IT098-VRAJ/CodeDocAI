"""
styles.py -- CodeDocAI
Single source of truth for all CSS design tokens and component styles.
Call inject_css() exactly once, immediately after st.set_page_config().
"""

import streamlit as st


def inject_css() -> None:
    """
    Inject the application's entire CSS block via st.markdown.
    Must be called before any other st.* render call.
    """
    st.markdown(
        """
    <style>
    /* -- Google Fonts (single import -- never duplicate) -- */
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;0,9..144,700;1,9..144,400&family=IBM+Plex+Mono:wght@400;500&display=swap');

    /* -- Design tokens -- */
    :root {
        --bg:             #000000;
        --surface:        #0A0A0A;
        --text-primary:   #F0EAD9;
        --text-muted:     #A59C8A;
        --border:         #222222;
        --accent-amber:   #E8B339;
        --accent-red:     #E5484D;

        --space-1:  4px;
        --space-2:  8px;
        --space-3:  16px;
        --space-4:  24px;
        --space-5:  32px;
        --space-6:  48px;

        --radius-pill:  999px;
        --radius-md:    12px;
        --radius-lg:    16px;
    }

    /* -- Global resets -- */
    html, body, [class*="css"], .stApp, .block-container {
        background-color: var(--bg) !important;
        color:            var(--text-primary) !important;
        font-family:      'IBM Plex Mono', monospace !important;
    }

    /* -- Heading elements use Fraunces -- */
    h1, h2, h3, h4, h5, h6,
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        font-family: 'Fraunces', serif !important;
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
    #MainMenu, footer, header {
        visibility: hidden !important;
        height: 0 !important;
        min-height: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
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
        font-family: 'IBM Plex Mono', monospace;
        font-size: 11px;
        font-weight: 500;
        color: var(--text-muted);
        line-height: 1.4;
    }
    .type-specimen {
        padding: var(--space-3) 0;
        border-bottom: 1px solid var(--border);
    }
    .type-label {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 10px;
        font-weight: 400;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.1em;
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
        border-radius: 2px;
    }
    .spacing-label {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 11px;
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
        font-family: 'IBM Plex Mono', monospace;
        font-size: 11px;
        font-weight: 500;
        color: var(--text-muted);
    }
    .section-header {
        font-family: 'Fraunces', serif !important;
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--text-primary);
        margin: var(--space-5) 0 var(--space-2);
        padding-bottom: var(--space-2);
        border-bottom: 1px solid var(--border);
    }
    .page-title {
        font-family: 'Fraunces', serif !important;
        font-size: 2rem;
        font-weight: 700;
        color: var(--accent-amber);
        margin-bottom: var(--space-2);
        letter-spacing: -0.02em;
    }
    .page-subtitle {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.8rem;
        font-weight: 400;
        color: var(--text-muted);
        margin-bottom: var(--space-5);
    }
    .foundation-footer {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.75rem;
        font-weight: 400;
        color: var(--text-muted);
        border-top: 1px solid var(--border);
        padding-top: var(--space-4);
        margin-top: var(--space-6);
        text-align: center;
    }
    .no-shadow-note {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.78rem;
        color: var(--text-muted);
        margin-top: var(--space-2);
    }

    /* ================================================================
       SESSION 1 -- Landing screen
       ================================================================ */

    .masthead-wordmark {
        font-family: 'Fraunces', serif;
        font-weight: 700;
        font-size: 1.4rem;
        color: var(--text-primary);
        letter-spacing: -0.02em;
        line-height: 1;
    }
    /* SCAN READY pill -- decorative, not clickable */
    .scan-ready-pill {
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 500;
        font-size: 0.65rem;
        letter-spacing: 0.12em;
        color: var(--accent-amber);
        background-color: rgba(232, 179, 57, 0.15);
        border: none;
        border-radius: var(--radius-pill);
        padding: 6px var(--space-3);
        cursor: default;
        user-select: none;
        pointer-events: none;
        line-height: 1;
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
        font-family: 'Fraunces', serif;
        font-weight: 700;
        font-size: 2.4rem;
        color: var(--text-primary);
        line-height: 1.1;
        letter-spacing: -0.03em;
        margin-bottom: var(--space-4);
    }
    .hero-subhead {
        font-family: 'Fraunces', serif;
        font-weight: 400;
        font-size: 1.05rem;
        color: var(--text-muted);
        line-height: 1.65;
        margin-bottom: var(--space-4); /* Reduced from space-6 to pull CTA closer */
    }

    /* CTA button: override Streamlit default chrome (solid primary CTA) */
    .stButton > button,
    .stDownloadButton > button,
    .stFormSubmitButton > button {
        font-family: 'IBM Plex Mono', monospace !important;
        font-weight: 500 !important;
        font-size: 0.8rem !important;
        line-height: 1 !important;
        letter-spacing: 0.1em !important;
        color: #151515 !important;
        background-color: var(--accent-amber) !important;
        border: none !important;
        border-radius: var(--radius-md) !important;
        padding: 11px var(--space-4) 19px var(--space-4) !important;
        cursor: pointer !important;
        transition: opacity 0.15s ease !important;
        width: auto !important;
        white-space: nowrap !important;
        text-align: center !important;
        justify-content: center !important;
        align-items: center !important;
        font-feature-settings: 'liga' 0, 'calt' 0 !important;
        font-variant-ligatures: none !important;
    }
    .stButton > button:hover,
    .stDownloadButton > button:hover,
    .stFormSubmitButton > button:hover {
        opacity: 0.88 !important;
        background-color: var(--accent-amber) !important;
        color: #151515 !important;
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
        outline: none !important;
        box-shadow: 0 0 0 2px var(--bg), 0 0 0 4px var(--accent-amber) !important;
    }

    /* Secondary button styling (outline/ghost) */
    button[data-testid="baseButton-secondary"],
    button[kind="secondary"],
    .stButton > button[data-testid="baseButton-secondary"],
    .stButton > button[kind="secondary"],
    div.element-container:has(#cta-secondary-marker-ns) + div .stButton > button,
    div.element-container:has(#cta-secondary-marker) + div .stButton > button {
        background-color: transparent !important;
        color: var(--accent-amber) !important;
        border: 1px solid var(--accent-amber) !important;
    }
    button[data-testid="baseButton-secondary"]:hover,
    button[kind="secondary"]:hover,
    .stButton > button[data-testid="baseButton-secondary"]:hover,
    .stButton > button[kind="secondary"]:hover,
    div.element-container:has(#cta-secondary-marker-ns) + div .stButton > button:hover,
    div.element-container:has(#cta-secondary-marker) + div .stButton > button:hover {
        background-color: rgba(232, 179, 57, 0.08) !important;
        color: var(--accent-amber) !important;
        border-color: var(--accent-amber) !important;
        opacity: 1 !important;
    }
    button[data-testid="baseButton-secondary"]:active,
    button[kind="secondary"]:active,
    .stButton > button[data-testid="baseButton-secondary"]:active,
    .stButton > button[kind="secondary"]:active,
    div.element-container:has(#cta-secondary-marker-ns) + div .stButton > button:active,
    div.element-container:has(#cta-secondary-marker) + div .stButton > button:active {
        background-color: transparent !important;
        opacity: 0.65 !important;
    }

    /* Landing footer -- kept in CSS for Session 0 foundation page; unused on landing */
    .landing-footer {
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 400;
        font-size: 0.68rem;
        letter-spacing: 0.08em;
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
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 400;
        font-size: 0.68rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: var(--text-muted);
        margin-top: 8px !important; /* Ensures breathing room below dividers */
        margin-bottom: var(--space-3);
    }

    /* Section A -- Why this exists (stacked layout with optimal reading width) */
    .why-section {
        padding: var(--space-4) 0 0 0; /* Stripped bottom padding completely */
    }
    .why-body {
        font-family: 'Fraunces', serif;
        font-weight: 400;
        font-size: 1.0625rem;  /* ~17px */
        color: var(--text-muted);
        line-height: 1.65;
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
        overflow: hidden;
        white-space: nowrap; /* Forces single line for the effect */
        border-right: 3px solid var(--accent-amber);
        max-width: 0;
        animation: typeMainline 1.2s steps(45, end) 0.2s forwards, blinkCursorMain 0.6s step-end 3 forwards;
    }
    @keyframes typeMainline {
        to { max-width: 100%; }
    }
    @keyframes blinkCursorMain {
        0%, 100% { border-right-color: transparent; }
        50% { border-right-color: var(--accent-amber); }
    }
    @media (max-width: 768px) {
        /* Mobile fallback so long headlines can wrap naturally */
        .typewriter-headline {
            white-space: normal;
            border-right: none;
            max-width: none;
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
    .security-item h4 {
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.72rem;
        color: var(--accent-amber) !important;
        margin-bottom: var(--space-2);
        letter-spacing: 0.05em;
    }
    .security-item p {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.68rem;
        color: var(--text-muted);
        line-height: 1.5;
        margin: 0;
    }

    /* -- Rationale 2-Column Grid -- */
    .rationale-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: var(--space-5);
        margin-top: var(--space-4);
    }
    @media (max-width: 650px) { .rationale-grid { grid-template-columns: 1fr; } }
    .rationale-col h3 {
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.78rem;
        letter-spacing: 0.1em;
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
    @media (max-width: 650px) { .caps-grid { grid-template-columns: 1fr; } }
    .caps-item {
        background: transparent;
        padding: var(--space-4) 0 0 0;
        border-top: 1px solid var(--border);
    }
    .caps-item h4 {
        font-family: 'Fraunces', serif !important;
        font-size: 1.15rem;
        color: var(--text-primary) !important;
        margin-bottom: var(--space-2);
        letter-spacing: -0.01em;
    }
    .caps-item p {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.75rem;
        color: var(--text-muted);
        line-height: 1.6;
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
        font-family: 'IBM Plex Mono', monospace;
    }
    .mock-editor-bar {
        background-color: #050505;
        border-bottom: 1px solid var(--border);
        padding: 10px 14px;
        display: flex;
        align-items: center;
        gap: 6px;
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
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.72rem;
    }
    .mock-editor-body {
        padding: var(--space-3) var(--space-4);
    }
    .mock-line {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.78rem;
        line-height: 1.6;
        display: flex;
        white-space: pre;
    }
    .mock-editor-status {
        border-top: 1px solid var(--border);
        padding: var(--space-2) var(--space-4);
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.68rem;
        color: var(--accent-amber);
    }
    .mock-editor-lineno {
        display: inline-block;
        width: 1.8rem;
        color: var(--text-muted);
        opacity: 0.5;
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
        0%, 70% { content: "> CodeT5 model initialized..."; color: var(--text-muted); }
        71%, 100% { content: "0.4s · docstring generated."; color: #4CAF50; }
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
        content: "> CodeT5 model initialized...";
        /* Extended the total time to 5.5s so the green success state triggers AFTER typing finishes */
        animation: statusSwap 5.5s forwards;
    }

    /* -- Timeline Hover Polish -- */
    .timeline-item {
        transition: background-color 0.2s ease, transform 0.2s ease;
        border-radius: var(--radius-md);
        padding: var(--space-4) !important;
        margin-left: -var(--space-4); /* Offset the padding for alignment */
    }
    .timeline-item:hover {
        background-color: #111111; /* Subtle tactile hover */
    }

    /* Sections B+C -- Unified Process + Built-With card */
    .process-card {
        background-color: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
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
        gap: 32px;
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
        gap: 2px;
    }
    .timeline-index {
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 500;
        font-size: 0.68rem;
        color: var(--accent-amber);
        line-height: 1;
    }
    .timeline-step {
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 700;
        font-size: 0.72rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: var(--text-primary);
        line-height: 1;
    }
    .timeline-desc {
        font-family: 'Fraunces', serif;
        font-weight: 400;
        font-size: 0.9375rem;
        color: var(--text-muted);
        line-height: 1.5;
        padding-top: 0;
    }
    /* Built-with inside card */
    .card-built-label {
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 400;
        font-size: 0.68rem;
        letter-spacing: 0.12em;
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
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 400;
        font-size: 0.72rem;
        letter-spacing: 0.06em;
        color: #FFFFFF !important;
        border: 1px solid var(--border);
        border-radius: var(--radius-pill);
        padding: var(--space-1) 10px !important;
        cursor: default;
        user-select: none;
        pointer-events: none;
        display: inline-block;
        line-height: 1;
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
        font-family: 'Fraunces', serif !important;
        font-weight: 400;
        font-size: 1.45rem;
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
    div:has(#cta-secondary-marker) + div .stButton > button:hover,
    div:has(#cta-secondary-marker-ask) + div .stButton > button:hover,
    div:has(#cta-secondary-marker-ns) + div .stButton > button:hover {
        background-color: rgba(232, 179, 57, 0.08) !important;
        color: var(--accent-amber) !important;
        opacity: 1 !important;
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
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 400;
        font-size: 0.68rem;
        color: var(--text-primary);
        letter-spacing: 0.05em;
        margin-top: -12px;
        margin-bottom: var(--space-5);
        background: rgba(255, 255, 255, 0.03); /* Subtle dark tint */
        border-left: 2px solid var(--accent-amber);
        padding: 8px 12px;
        border-radius: 0 4px 4px 0;
    }
    
    div.element-container:has(.scan-microcopy) {
        margin-top: -12px !important;
        margin-bottom: var(--space-4) !important;
    }
    .scan-microcopy {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.68rem;
        color: var(--text-muted);
        background: rgba(232, 179, 57, 0.05); /* Amber tint */
        border: 1px solid rgba(232, 179, 57, 0.2);
        padding: 8px 12px;
        border-radius: 4px;
        display: flex;
        align-items: flex-start;
        gap: 8px;
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
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 500;
        font-size: 0.68rem;
        letter-spacing: 0.05em;
        color: var(--text-muted);
        background: transparent; /* Stripped heavy boxes */
        padding: 0;
        border: none;
    }
    .scan-preview-arrow {
        color: var(--border);
        font-size: 0.8rem;
    }
    
    div.element-container:has(.scan-security-tag) {
        margin-top: -8px !important;
    }
    .scan-security-tag {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.65rem;
        color: var(--text-muted);
        display: flex;
        align-items: center;
        gap: 8px;
        background: rgba(76, 175, 80, 0.05); /* Green tint */
        border: 1px solid rgba(76, 175, 80, 0.2);
        padding: 8px 12px;
        border-radius: 4px;
    }

    .scan-input-section {
        padding: var(--space-5) 0 var(--space-4);
    }
    .scan-intro {
        font-family: 'Fraunces', serif;
        font-weight: 400;
        font-size: 1.0625rem;
        color: var(--text-muted);
        line-height: 1.65;
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
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 400;
        font-size: 0.68rem;
        letter-spacing: 0.16em;
        color: var(--text-muted);
        flex-shrink: 0;
    }
    .scan-helper {
        font-family: 'Fraunces', serif !important;
        font-weight: 400;
        font-size: 1.05rem;
        line-height: 1.65;
        color: var(--text-muted);
        margin-top: 0 !important; /* Tuck tightly against the button */
    }
    .scan-error-line {
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 400;
        font-size: 0.78rem;
        color: var(--accent-red);
        margin-top: var(--space-3);
    }
    .scan-results-section {
        padding: 0 !important; /* Strip the 48px var(--space-6) top padding */
        margin-top: var(--space-4) !important; /* Reduced from 32px */
    }
    .scan-summary {
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 400;
        font-size: 0.78rem;
        color: var(--text-muted);
        margin-bottom: 32px !important;
    }
    /* Direct row hover with a visible opacity */
    .ledger-row {
        border-top: 1px solid var(--border);
        display: grid;
        grid-template-columns: 2.5rem 1fr auto;
        gap: var(--space-4);
        padding: 12px 12px !important; /* Tighter padding for vertical balance */
        align-items: center !important;
        margin: 0 !important;
        transition: background-color 0.15s ease;
    }

    .ledger-row:hover {
        background-color: rgba(255, 255, 255, 0.08) !important;
        border-radius: 4px;
        cursor: default;
    }
    .ledger-row:last-child {
        border-bottom: 1px solid var(--border);
    }
    .ledger-index {
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 500;
        font-size: 0.72rem;
        color: var(--accent-amber);
        line-height: 1;
    }
    .ledger-path {
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 400;
        font-size: 0.78rem;
        color: var(--text-primary);
        line-height: 1.4;
        word-break: break-all;
    }
    .ledger-meta-missing {
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 500;
        font-size: 0.72rem;
        color: var(--accent-amber);
        line-height: 1;
        white-space: nowrap;
        text-align: right;
    }
    .ledger-meta-clean {
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 400;
        font-size: 0.72rem;
        color: var(--text-muted);
        line-height: 1;
        white-space: nowrap;
        text-align: right;
    }
    /* Tightly group the primary CTA with the estimate section */
    div:has(#cta-generate-marker) + div {
        margin-top: 0 !important; /* Rely entirely on Streamlit's neutralized natural gap */
    }
    .stFileUploader label,
    .stTextInput label {
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.72rem !important;
        font-weight: 400 !important;
        letter-spacing: 0.08em !important;
        color: var(--text-muted) !important;
        text-transform: uppercase !important;
    }
    .stFileUploader > div,
    .stTextInput > div > div {
        background-color: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-md) !important;
    }
    .stTextInput input {
        background-color: var(--surface) !important;
        color: var(--text-primary) !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.85rem !important;
        border: none !important;
        border-radius: var(--radius-md) !important;
    }
    /* Absolute override for Streamlit input placeholders */
    div[data-testid="stTextInput"] input::-webkit-input-placeholder {
        color: #A0A0A0 !important;
        opacity: 1 !important;
        -webkit-text-fill-color: #A0A0A0 !important;
    }
    div[data-testid="stTextInput"] input::-moz-placeholder {
        color: #A0A0A0 !important;
        opacity: 1 !important;
    }
    div[data-testid="stTextInput"] input::placeholder {
        color: #A0A0A0 !important;
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
        border-color: var(--accent-amber) !important;
        box-shadow: none !important;
    }

    /* Hide Streamlit form submission helper text */
    div[data-testid="InputInstructions"] {
        display: none !important;
    }

    /* Absolute override for Streamlit Expander content padding */
    div[data-testid="stExpanderDetails"],
    div[data-testid="stExpander"] details > div {
        padding-top: 24px !important;
    }

    /* -- Severity Pips (Scan Ledger) -- */
    .severity-pip {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 10px;
        vertical-align: middle;
        transform: translateY(-1px);
    }
    .pip-green { background-color: #4CAF50; }
    .pip-amber { background-color: var(--accent-amber); }
    .pip-red { background-color: var(--accent-red); }

    .system-note {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.68rem;
        color: var(--text-muted);
        margin-top: var(--space-4);
        padding-top: var(--space-3);
        border-top: 1px dashed rgba(255, 255, 255, 0.1);
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
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        background: var(--surface);
        padding: var(--space-3) var(--space-4);
    }
    @media (max-width: 650px) { 
        .telemetry-grid { grid-template-columns: 1fr; gap: var(--space-4); } 
    }
    .telemetry-col {
        display: flex;
        flex-direction: column;
        gap: 6px;
    }
    .tel-label {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.6rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: var(--text-muted);
    }
    .tel-value {
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 500;
        font-size: 0.72rem;
        color: var(--accent-amber);
    }

    /* Fraunces intro line (same treatment as .scan-intro / .why-body) */
    .gen-intro {
        font-family: 'Fraunces', serif;
        font-weight: 400;
        font-size: 1.0625rem;
        color: var(--text-muted);
        line-height: 1.65;
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
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 400;
        font-size: 0.68rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: var(--text-muted);
        margin-bottom: var(--space-2);
    }

    /* Summary / file-count line */
    .gen-outcome-summary {
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 400;
        font-size: 0.78rem;
        color: var(--text-muted);
        margin-bottom: var(--space-3);
    }

    /* -- Generation Outcome Sub-summary -- */
    .gen-outcome-sub {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.72rem;
        color: var(--text-muted);
        margin-top: var(--space-2);
        line-height: 1.5;
    }

    /* Rate-limit error message */
    .gen-error-msg {
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 400;
        font-size: 0.78rem;
        color: var(--accent-red);
        margin-bottom: var(--space-3);
        line-height: 1.55;
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
        font-family: 'Fraunces', serif;
        font-weight: 700;
        font-size: 1.25rem;
        color: var(--text-primary);
        margin: var(--space-6) 0 var(--space-3) 0;
    }
    .docs-empty-sub {
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 400;
        font-size: 0.78rem;
        color: var(--text-muted);
        margin-bottom: var(--space-5);
    }

    /* All-clean state message */
    .docs-all-clean {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.8rem;
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
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 400;
        font-size: 0.78rem;
        color: var(--text-muted);
        padding: var(--space-2) 0; /* Reduced padding */
        border: none !important;
    }
    .docs-clean-line:last-of-type {
        border: none !important;
    }
    .docs-file-path {
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 500;
        font-size: 0.78rem;
        color: var(--accent-amber);
        letter-spacing: 0.04em;
        margin-bottom: var(--space-2);
    }

    /* Module overview paragraph */
    .docs-overview {
        font-family: 'Fraunces', serif;
        font-weight: 400;
        font-size: 1.0625rem;
        color: var(--text-muted);
        line-height: 1.65;
        margin: 0 0 var(--space-5) 0;
        overflow: hidden;
    }

    /* Fixed Drop Cap typography */
    .docs-overview.drop-cap::first-letter {
        font-family: 'Fraunces', serif;
        font-weight: 700;
        font-size: 3.5em !important;
        line-height: 0.8 !important;
        margin-right: 8px !important;
        margin-top: 4px !important;
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
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 500;
        font-size: 0.85rem;
        color: var(--text-primary);
        line-height: 1;
    }

    .ai-draft-badge {
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 500;
        font-size: 0.58rem;
        letter-spacing: 0.1em;
        color: var(--accent-amber);
        border: 1px solid var(--accent-amber);
        border-radius: var(--radius-pill);
        padding: 2px 12px !important; /* Increased horizontal padding */
        cursor: default;
        user-select: none;
        pointer-events: none;
        line-height: 1;
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
    @media (max-width: 580px) {
        .docs-fn-cols {
            grid-template-columns: 1fr;
        }
    }

    /* Docstring column */
    .docs-docstring {
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 400;
        font-size: 0.75rem;
        color: var(--text-muted);
        line-height: 1.65;
    }

    /* Premium structured code blocks - Bypassing Streamlit's native <pre> styles */
    div[data-testid="stMarkdownContainer"] pre.docs-source-pre,
    .docs-source-pre {
        background: #121212 !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 8px !important;
        padding: 16px !important;
        margin: 0 !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.72rem !important;
        color: var(--text-muted) !important;
        line-height: 1.6 !important;
        white-space: pre-wrap !important;
        word-break: break-all !important;
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
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.65rem;
        color: var(--text-muted);
        letter-spacing: 0.05em;
        border-bottom: 1px solid var(--border);
        padding-bottom: var(--space-3);
        margin-bottom: var(--space-4);
        margin-top: -8px; /* Tucks it closer to the file path */
    }
    .docs-download-context {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.65rem;
        color: var(--text-muted);
        text-align: center;
        margin-bottom: var(--space-3);
        opacity: 0.8;
    }

    /* ================================================================
       SESSION 5 -- Q&A screen
       ================================================================ */

    /* -- Q&A Screen Polish -- */
    .vector-status-bar {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.68rem;
        color: var(--text-muted);
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 8px 12px;
        margin-bottom: var(--space-4);
        display: inline-flex;
        align-items: center;
        gap: 8px;
    }
    .vector-active-dot {
        color: #4CAF50;
        font-size: 0.8rem;
        line-height: 1;
    }
    .qa-disclaimer {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.65rem;
        color: var(--text-muted);
        text-align: center;
        opacity: 0.7;
        margin-top: var(--space-2);
    }
    div.element-container:has(.qa-disclaimer) {
        margin-top: -1.2rem !important; /* Pulls disclaimer tightly under the input form */
    }

    /* Intro line (shown only when qa_chat_history is empty) */
    .qa-intro {
        font-family: 'Fraunces', serif;
        font-weight: 400;
        font-size: 1.0625rem;
        color: var(--text-muted);
        line-height: 1.65;
        margin: 0 0 var(--space-4) 0; /* Reduced from space-5 */
    }

    /* Example questions label */
    .qa-chips-label {
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 400;
        font-size: 0.68rem;
        letter-spacing: 0.12em;
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
        font-family: 'Fraunces', serif !important;
        font-weight: 400 !important;
        font-size: 0.85rem !important; /* Slightly smaller for a chip feel */
        padding: 8px 16px !important; /* Sleek vertical padding */
        width: 100% !important;
        height: auto !important; /* Let height shrink to fit */
        line-height: 1.4 !important;
        white-space: normal !important;
        text-align: left !important; /* Force text to the left */
        justify-content: flex-start !important; /* Force flex children to the left */
        transition: border-color 0.15s ease, background-color 0.15s ease !important;
    }
    div:has(.qa-chip-marker) + div .stButton > button:hover {
        border-color: var(--accent-amber) !important;
        background-color: rgba(232, 179, 57, 0.06) !important;
        color: var(--accent-amber) !important;
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
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 500;
        font-size: 0.85rem;
        line-height: 1;
    }
    .qa-q-label {
        color: var(--accent-amber);
    }
    .qa-a-label {
        color: var(--text-muted);
    }
    .qa-q-text {
        font-family: 'Fraunces', serif;
        font-weight: 700;
        font-size: 1.15rem;
        color: var(--text-primary);
        line-height: 1.35;
        letter-spacing: -0.01em;
    }
    .qa-a-body {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        gap: var(--space-2);
    }
    .qa-a-text {
        font-family: 'Fraunces', serif;
        font-weight: 400;
        font-size: 1.05rem;
        color: var(--text-primary);
        line-height: 1.6;
    }
    .qa-a-fallback {
        color: var(--text-muted) !important;
    }

    /* Citation pill -- amber outline mono pill */
    .qa-citation-pill {
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 500;
        font-size: 0.65rem;
        letter-spacing: 0.08em;
        color: var(--accent-amber);
        border: 1px solid var(--accent-amber);
        border-radius: var(--radius-pill);
        padding: 3px 10px;
        cursor: default;
        user-select: none;
        pointer-events: none;
        line-height: 1;
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
    div[data-testid="stForm"] {
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
    .stFileUploader button,
    [data-testid="stFileUploaderDropzone"] button,
    [data-testid="stFileUploader"] [data-testid="stBaseButton-secondary"] {
        background-color: transparent !important;
        color: var(--accent-amber) !important;
        border: 1px solid var(--accent-amber) !important;
        border-radius: var(--radius-md) !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-weight: 500 !important;
        font-size: 0.75rem !important;
        letter-spacing: 0.08em !important;
        padding: var(--space-2) var(--space-4) !important;
        transition: background-color 0.15s ease, opacity 0.15s ease !important;
    }
    .stFileUploader button:hover,
    [data-testid="stFileUploaderDropzone"] button:hover,
    [data-testid="stFileUploader"] [data-testid="stBaseButton-secondary"]:hover {
        background-color: rgba(232, 179, 57, 0.08) !important;
        color: var(--accent-amber) !important;
        opacity: 1 !important;
    }

    /* ================================================================
       SESSION 6a -- Nav rail, Jump list, Estimates, Syntax highlighting
       ================================================================ */

    /* Expander styling in Scan screen */
    .stExpander {
        background-color: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-md) !important;
        margin-top: var(--space-2) !important;
        margin-bottom: var(--space-4) !important;
    }
    .stExpander details {
        border: none !important;
    }
    .stExpander summary {
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.72rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.08em !important;
        color: var(--text-muted) !important;
        text-transform: uppercase !important;
    }
    .stExpander summary:hover {
        color: var(--accent-amber) !important;
    }

    /* Nav rail Wordmark button -- scoped to column containing #rail-wordmark */
    div[data-testid="column"]:has(#rail-wordmark) .stButton > button,
    div[data-testid="stColumn"]:has(#rail-wordmark) .stButton > button,
    div[data-testid="column"]:has(#rail-wordmark) .stButton > button *,
    div[data-testid="stColumn"]:has(#rail-wordmark) .stButton > button * {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 !important;
        font-family: 'Fraunces', Georgia, serif !important;
        font-weight: 700 !important;
        font-size: 1.4rem !important;
        color: var(--text-primary) !important;
        letter-spacing: -0.02em !important;
        line-height: 1 !important;
        cursor: pointer !important;
        text-align: left !important;
        width: auto !important;
        white-space: nowrap !important;
        font-feature-settings: normal !important;
        font-variant-ligatures: normal !important;
        box-shadow: none !important;
        outline: none !important;
    }
    div[data-testid="column"]:has(#rail-wordmark) .stButton > button:hover,
    div[data-testid="stColumn"]:has(#rail-wordmark) .stButton > button:hover,
    div[data-testid="column"]:has(#rail-wordmark) .stButton > button:hover *,
    div[data-testid="stColumn"]:has(#rail-wordmark) .stButton > button:hover * {
        color: var(--accent-amber) !important;
        background: transparent !important;
        opacity: 1 !important;
    }

    /* Nav rail step buttons -- scoped to columns containing each step marker */
    div[data-testid="column"]:has(#rail-step-scan) .stButton > button,
    div[data-testid="stColumn"]:has(#rail-step-scan) .stButton > button,
    div[data-testid="column"]:has(#rail-step-scan) .stButton > button *,
    div[data-testid="stColumn"]:has(#rail-step-scan) .stButton > button *,
    div[data-testid="column"]:has(#rail-step-generate) .stButton > button,
    div[data-testid="stColumn"]:has(#rail-step-generate) .stButton > button,
    div[data-testid="column"]:has(#rail-step-generate) .stButton > button *,
    div[data-testid="stColumn"]:has(#rail-step-generate) .stButton > button *,
    div[data-testid="column"]:has(#rail-step-docs) .stButton > button,
    div[data-testid="stColumn"]:has(#rail-step-docs) .stButton > button,
    div[data-testid="column"]:has(#rail-step-docs) .stButton > button *,
    div[data-testid="stColumn"]:has(#rail-step-docs) .stButton > button *,
    div[data-testid="column"]:has(#rail-step-qa) .stButton > button,
    div[data-testid="stColumn"]:has(#rail-step-qa) .stButton > button,
    div[data-testid="column"]:has(#rail-step-qa) .stButton > button *,
    div[data-testid="stColumn"]:has(#rail-step-qa) .stButton > button * {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 auto !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-weight: 500 !important;
        font-size: 0.72rem !important;
        letter-spacing: 0.1em !important;
        color: var(--text-primary) !important;
        cursor: pointer !important;
        text-align: center !important;
        line-height: 1 !important;
        text-transform: uppercase !important;
        width: auto !important;
        display: block !important;
        white-space: nowrap !important;
        box-shadow: none !important;
        outline: none !important;
        font-feature-settings: 'liga' 0, 'calt' 0 !important;
        font-variant-ligatures: none !important;
    }
    div[data-testid="column"]:has(#rail-step-scan) .stButton > button:hover,
    div[data-testid="stColumn"]:has(#rail-step-scan) .stButton > button:hover,
    div[data-testid="column"]:has(#rail-step-scan) .stButton > button:hover *,
    div[data-testid="stColumn"]:has(#rail-step-scan) .stButton > button:hover *,
    div[data-testid="column"]:has(#rail-step-generate) .stButton > button:hover,
    div[data-testid="stColumn"]:has(#rail-step-generate) .stButton > button:hover,
    div[data-testid="column"]:has(#rail-step-generate) .stButton > button:hover *,
    div[data-testid="stColumn"]:has(#rail-step-generate) .stButton > button:hover *,
    div[data-testid="column"]:has(#rail-step-docs) .stButton > button:hover,
    div[data-testid="stColumn"]:has(#rail-step-docs) .stButton > button:hover,
    div[data-testid="column"]:has(#rail-step-docs) .stButton > button:hover *,
    div[data-testid="stColumn"]:has(#rail-step-docs) .stButton > button:hover *,
    div[data-testid="column"]:has(#rail-step-qa) .stButton > button:hover,
    div[data-testid="stColumn"]:has(#rail-step-qa) .stButton > button:hover,
    div[data-testid="column"]:has(#rail-step-qa) .stButton > button:hover *,
    div[data-testid="stColumn"]:has(#rail-step-qa) .stButton > button:hover * {
        color: var(--accent-amber) !important;
        background: transparent !important;
        opacity: 1 !important;
    }

    /* Nav rail breadcrumb indicators */
    .rail-current {
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 500;
        font-size: 0.72rem;
        letter-spacing: 0.1em;
        color: var(--accent-amber);
        text-transform: uppercase;
        text-align: center;
        line-height: 1;
        border-bottom: 1px solid var(--accent-amber);
        padding-bottom: 2px;
        display: block;
        margin: 0 auto;
        white-space: nowrap !important;
    }
    .rail-muted {
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 400;
        font-size: 0.72rem;
        letter-spacing: 0.1em;
        color: var(--text-muted);
        text-transform: uppercase;
        text-align: center;
        line-height: 1;
        cursor: default;
        user-select: none;
        display: block;
        margin: 0 auto;
        white-space: nowrap !important;
    }
    .rail-arrow {
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 400;
        font-size: 0.72rem;
        color: var(--border);
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        height: 100% !important;
        line-height: 1 !important;
        user-select: none;
        white-space: nowrap !important;
        transform: translateY(-3px) !important; /* Stronger optical nudge UP */
    }
    .rail-arrow svg {
        display: block !important;
        margin: auto !important;
    }
    div.element-container:has(.nav-rail-divider) {
        margin-bottom: -1rem !important; /* Neutralize Streamlit's native gap */
    }
    .nav-rail-divider {
        border: none !important;
        border-top: 1px solid var(--border) !important;
        margin: var(--space-2) 0 0 0 !important; /* Zeroed bottom margin */
    }

    /* Scan pre-flight estimate */
    .scan-estimate-section {
        margin-top: var(--space-4) !important; /* Reduced from 32px */
        margin-bottom: 0 !important;
    }
    .scan-estimate-body {
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 400;
        font-size: 0.78rem;
        color: var(--text-muted);
        margin: 0;
    }
    .scan-estimate-clean {
        font-family: 'Fraunces', serif;
        font-weight: 400;
        font-size: 1.0625rem;
        color: var(--text-muted);
        line-height: 1.65;
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
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 400;
        font-size: 0.72rem;
        color: var(--text-primary) !important;
        text-decoration: none !important; /* Remove underline */
        background-color: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-md); /* Pill shape */
        padding: 6px 12px;
        transition: all 0.15s ease;
    }
    .docs-jump-link:hover {
        border-color: var(--accent-amber);
        color: var(--accent-amber) !important;
        background-color: rgba(232, 179, 57, 0.05);
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
        font-family: 'Fraunces', serif;
        font-weight: 700;
        font-size: 1.6rem !important; /* Reduced from 2rem */
        color: var(--accent-amber);
        letter-spacing: -0.02em;
        line-height: 1;
    }
    .export-stat-label {
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 400;
        font-size: 0.68rem;
        letter-spacing: 0.12em;
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
        font-family: 'Fraunces', serif;
        font-weight: 600;
        font-size: 1.45rem;
        color: var(--text-primary);
        line-height: 1.25;
        letter-spacing: -0.02em;
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
        border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
        align-items: start !important; /* Prevent text shifting */
    }
    .arch-step-label {
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 500;
        font-size: 0.72rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: var(--accent-amber);
        line-height: 1;
        white-space: nowrap;
    }
    .arch-step-body {
        font-family: 'Fraunces', serif;
        font-weight: 400;
        font-size: 1.0rem;
        color: var(--text-muted);
        line-height: 1.65;
        /* max-width removed to allow full horizontal span */
    }

    /* -- Architecture Screen Polish -- */
    .arch-io-tag {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.65rem;
        color: var(--accent-amber);
        margin-top: var(--space-3);
        letter-spacing: 0.05em;
        opacity: 0.85;
    }
    .arch-infra-telemetry {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.65rem;
        color: var(--text-muted);
        text-align: center;
        border-top: 1px dashed rgba(255, 255, 255, 0.1);
        padding-top: var(--space-4);
        margin-top: var(--space-6);
        margin-bottom: var(--space-4);
        letter-spacing: 0.05em;
        line-height: 1.6;
    }

    /* Nav rail -- 5th step: export */
    div[data-testid="column"]:has(#rail-step-export) .stButton > button,
    div[data-testid="stColumn"]:has(#rail-step-export) .stButton > button,
    div[data-testid="column"]:has(#rail-step-export) .stButton > button *,
    div[data-testid="stColumn"]:has(#rail-step-export) .stButton > button * {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 auto !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-weight: 500 !important;
        font-size: 0.72rem !important;
        letter-spacing: 0.1em !important;
        color: var(--text-primary) !important;
        cursor: pointer !important;
        text-align: center !important;
        line-height: 1 !important;
        text-transform: uppercase !important;
        width: auto !important;
        display: block !important;
        white-space: nowrap !important;
        box-shadow: none !important;
        outline: none !important;
        font-feature-settings: 'liga' 0, 'calt' 0 !important;
        font-variant-ligatures: none !important;
    }
    div[data-testid="column"]:has(#rail-step-export) .stButton > button:hover,
    div[data-testid="stColumn"]:has(#rail-step-export) .stButton > button:hover,
    div[data-testid="column"]:has(#rail-step-export) .stButton > button:hover *,
    div[data-testid="stColumn"]:has(#rail-step-export) .stButton > button:hover * {
        color: var(--accent-amber) !important;
        background: transparent !important;
        opacity: 1 !important;
    }

    /* Remove default Streamlit right-padding to make the masthead flush with the grid */
    div[data-testid="column"]:has(#masthead-how-it-works) {
        padding-right: 0 !important;
    }

    /* Bulletproof right-alignment for the masthead button */
    div:has(#masthead-how-it-works) + div,
    div:has(#masthead-how-it-works) + div > div,
    div:has(#masthead-how-it-works) + div .stButton {
        display: flex !important;
        justify-content: flex-end !important;
        width: 100% !important;
    }
    div:has(#masthead-how-it-works) + div .stButton > button {
        background-color: transparent !important;
        color: var(--accent-amber) !important;
        border: 1px solid var(--accent-amber) !important;
        font-size: 0.72rem !important;
        padding: var(--space-2) var(--space-3) !important;
        width: auto !important;
    }
    div:has(#masthead-how-it-works) + div .stButton > button:hover {
        background-color: rgba(232, 179, 57, 0.08) !important;
        color: var(--accent-amber) !important;
        opacity: 1 !important;
    }
    div:has(#masthead-how-it-works) + div .stButton > button:active {
        background-color: transparent !important;
        opacity: 0.65 !important;
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
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.75rem;
        color: var(--text-muted);
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: var(--space-4);
        margin-top: var(--space-4);
        margin-bottom: var(--space-5);
        line-height: 1.6;
        white-space: pre; /* Preserves the file tree spacing perfectly */
        overflow-x: auto;
    }
    .session-disclaimer {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.65rem;
        color: var(--text-muted);
        opacity: 0.7;
        margin-top: var(--space-4);
        text-align: left;
    }
    /* -- File Uploader Sleek Redesign -- */
    [data-testid="stFileUploaderDropzone"] {
        background-color: #050505 !important;
        border: 1px dashed var(--border) !important;
        border-radius: var(--radius-md) !important;
        padding: var(--space-4) !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stFileUploaderDropzone"]:hover,
    [data-testid="stFileUploaderDropzone"]:focus-within {
        border-color: var(--accent-amber) !important;
        background-color: rgba(232, 179, 57, 0.05) !important;
    }
    /* Style the uploaded file list item background */
    [data-testid="stUploadedFile"] {
        background-color: #050505 !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-md) !important;
    }
    /* Hide Streamlit's default giant cloud icon */
    [data-testid="stFileUploaderDropzone"] svg {
        display: none !important;
    }
    /* Restyle the small instruction text inside the dropzone */
    [data-testid="stFileUploaderDropzone"] small {
        font-family: 'IBM Plex Mono', monospace !important;
        color: var(--text-muted) !important;
        font-size: 0.72rem !important;
        letter-spacing: 0.05em !important;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )
