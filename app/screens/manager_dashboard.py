import streamlit as st
import pandas as pd
import json
import os

_AUDIT_FILE = "enterprise_audit.json"

def render():
    st.markdown('<div class="header-container"><h1 class="header-title">Corporate <span>Audit & Compliance Ledger</span></h1></div>', unsafe_allow_html=True)
    
    # Clearance check
    if st.session_state.get("role") != "manager":
        st.error("🚨 403 FORBIDDEN: You do not possess Managerial Clearance to inspect corporate audit telemetry.")
        if st.button("Return to Developer View"):
            st.session_state["current_screen"] = "landing"
            st.rerun()
        st.stop()

    st.markdown("### 🛡️ Real-Time Governance & Team Oversight")
    st.markdown("Continuous audit trail of repository scans, local CodeT5 batch inferences, and AI prompt surveillance.")

    logs = []
    if os.path.exists(_AUDIT_FILE):
        try:
            with open(_AUDIT_FILE, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except Exception:
            pass

    if not logs:
        st.info("The audit ledger is currently pristine. No events logged.")
        return

    df = pd.DataFrame(logs)
    
    # Ensure expected columns exist
    for col in ["timestamp", "user", "action", "severity", "details"]:
        if col not in df.columns:
            df[col] = "N/A"

    # --- TOP LEVEL TELEMETRY METRICS ---
    total_events = len(df)
    critical_events = len(df[df["severity"] == "CRITICAL"])
    qa_queries = len(df[df["action"] == "Q&A_QUERY"])
    active_users = df["user"].nunique()

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Total Logged Events", total_events)
    kpi2.metric("Active Employees", active_users)
    kpi3.metric("RAG Prompts Inspected", qa_queries)
    kpi4.metric("Security Incidents", critical_events, delta=f"{critical_events} flagged" if critical_events else "0", delta_color="inverse")

    st.markdown("---")

    # --- FILTER INTERFACE ---
    col_user, col_act, col_sev = st.columns(3)
    with col_user:
        users_list = ["All Users"] + sorted(list(df["user"].unique()))
        selected_user = st.selectbox("Filter by Employee:", users_list)
    with col_act:
        actions_list = ["All Actions"] + sorted(list(df["action"].unique()))
        selected_action = st.selectbox("Filter by Action:", actions_list)
    with col_sev:
        severities = ["All Severities", "CRITICAL", "WARNING", "INFO"]
        selected_sev = st.selectbox("Filter by Security Level:", severities)

    # Apply Filters for Dataframe Display
    filtered_df = df.copy()
    if selected_user != "All Users":
        filtered_df = filtered_df[filtered_df["user"] == selected_user]
    if selected_action != "All Actions":
        filtered_df = filtered_df[filtered_df["action"] == selected_action]
    if selected_sev != "All Severities":
        filtered_df = filtered_df[filtered_df["severity"] == selected_sev]

    filtered_df = filtered_df.sort_values(by="timestamp", ascending=False)
    
    st.dataframe(
        filtered_df[["timestamp", "user", "action", "severity", "details"]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "timestamp": st.column_config.TextColumn("UTC Timestamp", width="small"),
            "user": st.column_config.TextColumn("Engineer", width="small"),
            "action": st.column_config.TextColumn("Operation", width="small"),
            "severity": st.column_config.TextColumn("Severity", width="small"),
            "details": st.column_config.TextColumn("Logged Telemetry / Query Content", width="large"),
        }
    )

    # --- COMPLIANCE EXPORT & DATA PURGE ---
    st.markdown("---")
    col_dl, col_purge = st.columns([2, 1.5])
    
    with col_dl:
        csv_data = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ EXPORT AUDIT LOG (CSV)",
            data=csv_data,
            file_name="soc2_type2_telemetry_report.csv",
            mime="text/csv",
            type="secondary",
            use_container_width=True
        )
        
    with col_purge:
        purge_label = "🗑️ WIPE ENTIRE LEDGER" if selected_user == "All Users" else f"🗑️ PURGE '{selected_user.upper()}'"
        
        if st.button(purge_label, type="primary", use_container_width=True):
            if selected_user == "All Users":
                new_logs = []
            else:
                new_logs = [log for log in logs if log.get("user") != selected_user]
            
            try:
                with open(_AUDIT_FILE, "w", encoding="utf-8") as f:
                    json.dump(new_logs, f, indent=2)
            except Exception:
                pass
            st.rerun()