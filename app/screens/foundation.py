"""
screens/foundation.py -- CodeDocAI
Foundation verification screen renderer (Session 0 -- kept as acceptance artifact).
"""

import streamlit as st


def render_foundation() -> None:
    st.markdown(
        '<div class="page-title">CodeDocAI \u2014 Foundation Check</div>'
        '<div class="page-subtitle">Session 0 \u00B7 Design-token acceptance artifact</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="section-header">Colors</div>', unsafe_allow_html=True)
    COLOR_TOKENS = [
        ("--bg",           "#151515"),
        ("--surface",      "#14120F"),
        ("--text-primary", "#F0EAD9"),
        ("--text-muted",   "#A59C8A"),
        ("--border",       "#332E28"),
        ("--accent-amber", "#E8B339"),
        ("--accent-red",   "#E5484D"),
    ]
    swatches_html = '<div class="token-grid">'
    for token, hex_val in COLOR_TOKENS:
        swatches_html += (
            f'<div class="swatch">'
            f'<div class="swatch-block" style="background:{hex_val};"></div>'
            f'<div class="swatch-name">{token}<br>{hex_val}</div>'
            f'</div>'
        )
    swatches_html += '</div>'
    st.markdown(swatches_html, unsafe_allow_html=True)

    st.markdown('<div class="section-header">Typography</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="type-specimen">'
        '<div class="type-label">Fraunces - weight 700 - display heading</div>'
        '<div style="font-family:\'Fraunces\',serif;font-weight:700;font-size:2.4rem;'
        'color:var(--text-primary);line-height:1.15;letter-spacing:-0.02em;">CodeDocAI</div>'
        '</div>'
        '<div class="type-specimen">'
        '<div class="type-label">Fraunces - weight 400 - body serif</div>'
        '<div style="font-family:\'Fraunces\',serif;font-weight:400;font-size:1.15rem;'
        'color:var(--text-primary);line-height:1.5;">The quick brown fox jumps over the lazy dog</div>'
        '</div>'
        '<div class="type-specimen">'
        '<div class="type-label">IBM Plex Mono - weight 400 - label / pill</div>'
        '<div style="font-family:\'IBM Plex Mono\',monospace;font-weight:400;font-size:1rem;'
        'color:var(--text-primary);line-height:1.5;">scan &middot; docs &middot; ask</div>'
        '</div>'
        '<div class="type-specimen" style="border-bottom:none;">'
        '<div class="type-label">IBM Plex Mono - weight 500 - button / badge</div>'
        '<div style="font-family:\'IBM Plex Mono\',monospace;font-weight:500;font-size:1rem;'
        'color:var(--text-primary);line-height:1.5;">Ai draft</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-header">Spacing Scale</div>', unsafe_allow_html=True)
    SPACING = [
        ("--space-1", "4px",  4),
        ("--space-2", "8px",  8),
        ("--space-3", "16px", 16),
        ("--space-4", "24px", 24),
        ("--space-5", "32px", 32),
        ("--space-6", "48px", 48),
    ]
    spacing_html = '<div class="spacing-grid">'
    for var, label, px in SPACING:
        spacing_html += (
            f'<div class="spacing-item">'
            f'<div class="spacing-bar" style="height:{px}px;" title="{var}"></div>'
            f'<div class="spacing-label">{label}</div>'
            f'</div>'
        )
    spacing_html += '</div>'
    st.markdown(spacing_html, unsafe_allow_html=True)

    st.markdown('<div class="section-header">Borders &amp; Radius</div>', unsafe_allow_html=True)
    _RADIUS_ITEMS = [
        ("pill",           "border-radius:var(--radius-pill)", "80px",  "36px", "--radius-pill &middot; 999px"),
        ("md",             "border-radius:var(--radius-md)",   "110px", "64px", "--radius-md &middot; 12px"),
        ("lg",             "border-radius:var(--radius-lg)",   "110px", "64px", "--radius-lg &middot; 16px"),
        ("hairline border","border-radius:0",                  "110px", "64px", "1px solid var(--border)"),
    ]
    radius_html = '<div class="radius-grid">'
    for label, radius_style, w, h, note in _RADIUS_ITEMS:
        radius_html += (
            f'<div style="display:flex;flex-direction:column;align-items:center;gap:var(--space-1);">'
            f'<div class="radius-box" style="{radius_style};width:{w};height:{h};">'
            f'<span class="r-label">{label}</span>'
            f'</div>'
            f'<span class="spacing-label">{note}</span>'
            f'</div>'
        )
    radius_html += '</div>'
    radius_html += '<div class="no-shadow-note">&#x26A0;&#xFE0F;&nbsp; No box-shadow is used anywhere in this app.</div>'
    st.markdown(radius_html, unsafe_allow_html=True)

    st.markdown(
        '<div class="foundation-footer">Session 0 \u2014 Foundation only. Screens begin in Session 1.</div>',
        unsafe_allow_html=True,
    )
