import contextlib

import pandas as pd
import streamlit as st

from helpers import log_audit, page_heading, purge_audit_log, queue_toast, read_audit_log, render_stats

# Severity reads from an icon and a word as well as its colour.
SEVERITY_ICONS = {"CRITICAL": "▲", "WARNING": "◆", "INFO": "●"}
SEVERITY_COLOURS = {"CRITICAL": "#E5484D", "WARNING": "#E8B339", "INFO": "#A59C8A"}  # --color-danger, --accent-amber, --text-muted


def _severity_colour(value: str) -> str:
    level = str(value).split(" ")[-1]
    return f"color: {SEVERITY_COLOURS[level]}; font-weight: 500" if level in SEVERITY_COLOURS else ""


def _close_purge() -> None:
    st.session_state["_confirm_purge"] = None


@st.dialog("Delete audit entries?", on_dismiss=_close_purge)
def _purge_dialog(selected_user: str, doomed: int) -> None:
    scope = "the whole log" if selected_user == "All Users" else f"every entry of '{selected_user}'"
    st.markdown(
        f'<p class="dialog-body">This permanently deletes {doomed} entries ({scope}). '
        "It can’t be undone; download the CSV first if anyone might need the records.</p>",
        unsafe_allow_html=True,
    )
    with st.container(horizontal=True, horizontal_alignment="right", gap="small", key="purge_actions"):
        if st.button("Cancel", key="purge_cancel", type="secondary"):
            _close_purge()
            st.rerun()
        # The danger_* key gives this button the danger colour instead of the brand accent.
        if st.button(f"Delete {doomed} entries", key="danger_purge_confirm", type="primary"):
            deleted = purge_audit_log(None if selected_user == "All Users" else selected_user)
            _close_purge()
            # A purge is itself an auditable action: it leaves a record of who deleted what.
            log_audit(
                action="LEDGER_PURGE",
                details=f"Deleted {deleted} audit entries ({scope}).",
                user=st.session_state.get("username") or "manager",
                severity="WARNING",
            )
            queue_toast(f"Deleted {deleted} audit entries", ":material/delete:")
            st.rerun()


def _close_row() -> None:
    st.session_state["_audit_table_version"] = st.session_state.get("_audit_table_version", 0) + 1


@st.dialog("Audit entry", width="medium", on_dismiss=_close_row)
def _row_dialog(row: dict) -> None:
    render_stats([("Severity", row.get("severity", "")), ("Action", row.get("action", "")), ("User", row.get("user", ""))])
    st.caption(f"{row.get('timestamp', '')} UTC")
    st.text(str(row.get("details", "")))
    if st.button("Close", key="audit_row_close", type="secondary"):
        _close_row()
        st.rerun()


def render() -> None:
    page_heading("Audit log")

    # Role check
    if st.session_state.get("role") != "manager":
        st.error("Only the manager account can open the audit log.")
        if st.button("Back to the app", key="dashboard_denied_back", type="primary"):
            st.session_state["current_screen"] = "landing"
            st.rerun()
        st.stop()

    if st.button("Back to the app", key="dashboard_back", type="tertiary", icon=":material/arrow_back:"):
        st.session_state["current_screen"] = "landing"
        st.rerun()

    logs = read_audit_log()
    if not logs:
        st.info("No events yet.")
        return

    df = pd.DataFrame(logs)

    # Ensure expected columns exist
    for col in ["timestamp", "user", "action", "severity", "details"]:
        if col not in df.columns:
            df[col] = "N/A"

    # --- TOTALS ---
    total_events = len(df)
    critical_events = len(df[df["severity"] == "CRITICAL"])
    qa_queries = len(df[df["action"] == "Q&A_QUERY"])
    active_users = df["user"].nunique()

    render_stats([
        ("Events", total_events),
        ("Users", active_users),
        ("Questions asked", qa_queries),
        ("Critical", critical_events),
    ], key="audit_stats")

    # --- FILTERS ---
    col_user, col_act, col_sev = st.columns(3)
    with col_user:
        users_list = ["All Users", *sorted(df["user"].unique())]
        selected_user = st.selectbox("User", users_list)
    with col_act:
        actions_list = ["All Actions", *sorted(df["action"].unique())]
        selected_action = st.selectbox("Action", actions_list)
    with col_sev:
        severities = ["All Severities", "CRITICAL", "WARNING", "INFO"]
        selected_sev = st.selectbox("Severity", severities)

    # Apply Filters for Dataframe Display
    filtered_df = df.copy()
    if selected_user != "All Users":
        filtered_df = filtered_df[filtered_df["user"] == selected_user]
    if selected_action != "All Actions":
        filtered_df = filtered_df[filtered_df["action"] == selected_action]
    if selected_sev != "All Severities":
        filtered_df = filtered_df[filtered_df["severity"] == selected_sev]

    filtered_df = filtered_df.sort_values(by="timestamp", ascending=False)

    shown = filtered_df[["timestamp", "user", "action", "severity", "details"]].copy()
    shown["severity"] = shown["severity"].map(lambda s: f"{SEVERITY_ICONS.get(s, '·')} {s}")
    styled = shown.style.map(_severity_colour, subset=["severity"])
    selection = st.dataframe(
        styled,
        width="stretch",
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        key=f"audit_table_{st.session_state.get('_audit_table_version', 0)}",
        column_config={
            "timestamp": st.column_config.TextColumn("Time (UTC)", width="medium", pinned=True),
            "user": st.column_config.TextColumn("User", width="small"),
            "action": st.column_config.TextColumn("Action", width=190),
            "severity": st.column_config.TextColumn("Severity", width=120),
            "details": st.column_config.TextColumn("Details", width="large"),
        }
    )

    # The table cuts long details short, so a selected row opens in full in a dialog.
    selected_rows = []
    with contextlib.suppress(AttributeError, TypeError):
        selected_rows = list(selection.selection.rows)
    # Streamlit allows one open dialog per run, and the delete confirmation takes precedence.
    if selected_rows and selected_rows[0] < len(filtered_df) and not st.session_state.get("_confirm_purge"):
        _row_dialog(filtered_df.iloc[selected_rows[0]].to_dict())
    else:
        st.caption("Select a row to read it in full.")

    # --- DOWNLOAD & DELETE ---
    with st.container(horizontal=True, gap="small", key="audit_actions"):
        csv_data = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name="codedocai_audit_log.csv",
            mime="text/csv",
            type="secondary",
            icon=":material/download:",
        )
        purge_label = "Delete all entries" if selected_user == "All Users" else f"Delete entries of '{selected_user}'"

        doomed = len(logs) if selected_user == "All Users" else sum(1 for log in logs if log.get("user") == selected_user)
        if st.button(purge_label, type="secondary", disabled=doomed == 0, key="purge_open",
                     icon=":material/delete:"):
            st.session_state["_confirm_purge"] = selected_user
        if st.session_state.get("_confirm_purge") == selected_user and doomed:
            _purge_dialog(selected_user, doomed)

