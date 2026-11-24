import hashlib
import hmac

import streamlit as st

from helpers import log_audit, page_heading

# Demo accounts. Only a salted PBKDF2 hash of each password is kept here, so the source
# doesn't hand out working sign-ins; the passwords themselves are shared with the demo.
_HASH_ITERATIONS = 200_000

_ENTERPRISE_USERS = {
    "vraj": {"password_hash": "033fc1e4c6ee10fdc750e7a587919f3b3802bca13985417576aea8cde00b504d", "role": "developer", "title": "Staff Software Engineer"},
    "dev": {"password_hash": "2333cf9d1ae07ce6c00b3dd9d5fa8cbe6913a6c63ab43c141a706062d6b32411", "role": "developer", "title": "Backend Systems Engineer"},
    "meet": {"password_hash": "ac0fb1c3bba4870083f2bb0233959dc59acd2913117ce15cdac20cfcbee0e012", "role": "developer", "title": "Cloud & Infrastructure Engineer"},
    "veda": {"password_hash": "c18a6152a2471d34de6d4b6ecce54ac6f0285c8a06726145a43468c5d7ee1e8b", "role": "developer", "title": "Application Security Specialist"},
    "himanshi": {"password_hash": "f8bbc11e136b1f57b72d39589b5da91de252ab72cdb8dc219840230d2b244377", "role": "developer", "title": "Data Pipeline Engineer"},
    "smit": {"password_hash": "865c261e200b2d6aeb41f9df27d539aa749957448252bdcf1fc546bd311f1143", "role": "developer", "title": "Frontend Interface Lead"},
    "namita": {"password_hash": "2219ea578aca6027e63f2924b6e41b53af212923d190960a51ea1c47ecbdd1f1", "role": "developer", "title": "QA Automation Lead"},
    "admin": {"password_hash": "83e44237fd90f6d3436593a7ef539de53d5e5fb73f0ffbb53a806a54ac334df2", "role": "manager", "title": "VP of Engineering & Security"},
}

# The demo passwords are shown on the sign-in page on purpose; this list drives that list
# and the click-to-fill rows. Sign-in itself still checks the PBKDF2 hashes above.
DEMO_ACCOUNTS = [
    ("admin", "Manager", "admin@director"),
    ("vraj", "Developer", "corp@vraj2026"),
    ("dev", "Developer", "corp@dev2026"),
    ("meet", "Developer", "corp@meet2026"),
    ("veda", "Developer", "corp@veda2026"),
    ("himanshi", "Developer", "corp@himanshi2026"),
    ("smit", "Developer", "corp@smit2026"),
    ("namita", "Developer", "corp@namita2026"),
]


def _fill_form(username: str, password: str) -> None:
    st.session_state["login_username"] = username
    st.session_state["login_password"] = password


def _password_matches(username: str, password: str, entry: dict) -> bool:
    """Constant-time comparison of the typed password against the stored hash."""
    salt = f"codedocai-demo:{username}".encode()
    typed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, _HASH_ITERATIONS).hex()
    return hmac.compare_digest(typed, entry["password_hash"])


def _return_screen() -> str:
    """The screen the visitor was on before opening the sign-in page."""
    screen = st.session_state.get("_return_screen") or "landing"
    return "landing" if screen in ("login", "manager_dashboard") else screen


def render():
    wrap = st.container(horizontal=True, horizontal_alignment="center", key="login_wrap")
    with wrap, wrap.container(width=440, key="login_card"):
        _render_card()


def _render_card() -> None:
    # A way out that does not depend on the browser's back button.
    if st.button("Back", key="login_back", type="tertiary", icon=":material/arrow_back:"):
        st.session_state["current_screen"] = _return_screen()
        st.rerun()

    page_heading("Sign in", "Developers' activity is logged; the manager account reads the log.")

    # Collapsible credentials cheat sheet for presentation clarity
    with st.expander("Demo accounts: click one to fill the form", type="compact", key="compact_demo_accounts"):
        for username, role, password in DEMO_ACCOUNTS:
            st.button(
                f"`{username}` :gray[{role} · {password}]",
                key=f"login_fill_{username}",
                type="tertiary",
                width="stretch",
                on_click=_fill_form,
                args=(username, password),
            )

    with st.form("enterprise_sso_form", border=False):
        username = st.text_input("Username", placeholder="vraj, meet, admin", key="login_username").strip().lower()
        password = st.text_input("Password", type="password", key="login_password")
        submitted = st.form_submit_button("Sign in", type="primary", width="stretch")

        if submitted:
            user_entry = _ENTERPRISE_USERS.get(username)
            if user_entry and _password_matches(username, password, user_entry):
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.session_state["role"] = user_entry["role"]
                st.session_state["user_title"] = user_entry["title"]

                if user_entry["role"] == "manager":
                    st.session_state["current_screen"] = "manager_dashboard"
                    log_audit(
                        action="AUTH",
                        details=f"Manager '{username}' signed in.",
                        user=username,
                        severity="INFO"
                    )
                else:
                    # Back to where they were; a visitor who had not started yet goes to the scan step.
                    target = _return_screen()
                    st.session_state["current_screen"] = "scan" if target == "landing" else target
                    log_audit(
                        action="AUTH",
                        details=f"{user_entry['title']} '{username}' signed in.",
                        user=username,
                        severity="INFO"
                    )
                st.rerun()
            else:
                st.error("Wrong username or password.")
                log_audit(
                    action="SECURITY_VIOLATION",
                    details=f"Failed sign-in for username '{username}'.",
                    user=username if username else "anonymous",
                    severity="CRITICAL"
                )
