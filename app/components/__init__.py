"""
Inline Streamlit Components V2 (no iframe, no build step).

Each module registers its component once at import time and exposes a small
Python function that mounts it. Components render in a shadow root; they read
the app's design tokens (--accent-amber, --surface, ...) and Streamlit's --st-*
variables, which both inherit into the shadow root from the page.
"""
