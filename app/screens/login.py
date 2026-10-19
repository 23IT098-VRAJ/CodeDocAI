import streamlit as st

try:
    from helpers import log_audit
except ImportError:
    from app.helpers import log_audit

# Enterprise Corporate Directory
_ENTERPRISE_USERS = {
    "vraj": {"password": "corp@vraj2026", "role": "developer", "title": "Staff Software Engineer"},
    "dev": {"password": "corp@dev2026", "role": "developer", "title": "Backend Systems Engineer"},
    "meet": {"password": "corp@meet2026", "role": "developer", "title": "Cloud & Infrastructure Engineer"},
    "veda": {"password": "corp@veda2026", "role": "developer", "title": "Application Security Specialist"},
    "himanshi": {"password": "corp@himanshi2026", "role": "developer", "title": "Data Pipeline Engineer"},
    "smit": {"password": "corp@smit2026", "role": "developer", "title": "Frontend Interface Lead"},
    "namita": {"password": "corp@namita2026", "role": "developer", "title": "QA Automation Lead"},
    "admin": {"password": "admin@director", "role": "manager", "title": "VP of Engineering & Security"},
}

def render():
    st.markdown('<div class="header-container"><h1 class="header-title">CodeDocAI <span>Enterprise</span></h1></div>', unsafe_allow_html=True)
    st.markdown("### 🔐 SOC-2 / ISO-27001 Access Gateway")
    st.markdown("Role-based perimeter access for internal engineering teams and audit supervisors.")

    # Collapsible credentials cheat sheet for presentation clarity
    with st.expander("Corporate Directory Credentials (Click to inspect)"):
        st.markdown(
            "| Username | Role | Job Title | Password |\n"
            "|---|---|---|---|\n"
            "| `admin` | **Manager** | VP of Engineering | `admin@director` |\n"
            "| `vraj` | Developer | Staff Software Engineer | `corp@vraj2026` |\n"
            "| `dev` | Developer | Backend Systems Engineer | `corp@dev2026` |\n"
            "| `meet` | Developer | Cloud & Infrastructure | `corp@meet2026` |\n"
            "| `veda` | Developer | Application Security | `corp@veda2026` |\n"
            "| `himanshi` | Developer | Data Pipeline Engineer | `corp@himanshi2026` |\n"
            "| `smit` | Developer | Frontend Interface Lead | `corp@smit2026` |\n"
            "| `namita` | Developer | QA Automation Lead | `corp@namita2026` |"
        )

    with st.form("enterprise_sso_form"):
        username = st.text_input("Corporate ID (Username)", placeholder="e.g. vraj, meet, admin").strip().lower()
        password = st.text_input("Password / SSO Token", type="password")
        submitted = st.form_submit_button("AUTHENTICATE WITH SSO", type="primary", use_container_width=True)

        if submitted:
            user_entry = _ENTERPRISE_USERS.get(username)
            if user_entry and user_entry["password"] == password:
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.session_state["role"] = user_entry["role"]
                st.session_state["user_title"] = user_entry["title"]

                if user_entry["role"] == "manager":
                    st.session_state["current_screen"] = "manager_dashboard"
                    log_audit(
                        action="AUTH",
                        details=f"Engineering Manager '{username}' authenticated. Clearance: Superuser / Auditor.",
                        user=username,
                        severity="INFO"
                    )
                else:
                    st.session_state["current_screen"] = "scan"
                    log_audit(
                        action="AUTH",
                        details=f"{user_entry['title']} '{username}' authenticated via Enterprise SSO.",
                        user=username,
                        severity="INFO"
                    )
                st.rerun()
            else:
                st.error("❌ Authentication Denied: Invalid credentials or unassigned corporate identity.")
                log_audit(
                    action="SECURITY_VIOLATION",
                    details=f"Failed login attempt for account handle: '{username}'",
                    user=username if username else "anonymous",
                    severity="CRITICAL"
                )