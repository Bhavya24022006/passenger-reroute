import streamlit as st
import pandas as pd
import json
import subprocess

# Set page layout to wide
st.set_page_config(layout="wide")

# ==========================================
# SIDEBAR: LIVE BUSINESS RULE PROFILER
# ==========================================
st.sidebar.title("🛠️ Business Rule Engine")

# Load existing configuration rules
with open("rules_config.json", "r") as f:
    config = json.load(f)

st.sidebar.subheader("Passenger Priorities")
u_minor_score = st.sidebar.slider("Unaccompanied Minor Weight", 10, 100, int(config["passenger_priorities"]["UNACCOMPANIED_MINOR_SCORE"]))
emp_score = st.sidebar.slider("On-Duty Employee Weight", 10, 100, int(config["passenger_priorities"]["ON_DUTY_EMPLOYEE_SCORE"]))

st.sidebar.subheader("Routing Constraints")
allow_multihop_minors = st.sidebar.checkbox("Allow Multi-hop for Minors", value=config["constraints"]["ALLOW_MULTIHOP_FOR_MINORS"])

# Save and trigger recalculation sequence
if st.sidebar.button("💾 Apply Rules & Rerun Engine"):
    # Update config memory mapping structure
    config["passenger_priorities"]["UNACCOMPANIED_MINOR_SCORE"] = u_minor_score
    config["passenger_priorities"]["ON_DUTY_EMPLOYEE_SCORE"] = emp_score
    config["constraints"]["ALLOW_MULTIHOP_FOR_MINORS"] = allow_multihop_minors
    
    # Save configurations back out to root JSON
    with open("rules_config.json", "w") as f:
        json.dump(config, f, indent=2)
        
    st.sidebar.success("Rules updated! Running engine...")
    
    # Fire off core reaccommodation loop
    subprocess.run(["python", "reaccommodation.py"])
    
    # Clear cache to force Streamlit to read new data files
    st.cache_data.clear()
    st.sidebar.balloons()

# ==========================================
# MAIN DASHBOARD VIEW
# ==========================================
st.title("✈️ Airline Passenger Re-accommodation System")

# Helper loaders for updated runs (Cached until rules are reset)
@st.cache_data
def load_processed_data():
    try:
        df_assigned = pd.read_csv("data/processed/final_assignments_advanced.csv")
        df_exceptions = pd.read_csv("data/processed/exceptions_advanced.csv")
    except:
        df_assigned = pd.DataFrame()
        df_exceptions = pd.DataFrame()
    return df_assigned, df_exceptions

df_assigned, df_exceptions = load_processed_data()

total_assigned = len(df_assigned)
total_exceptions = len(df_exceptions)
total_impacted = total_assigned + total_exceptions

# High Level Performance KPIs
st.subheader("📊 Operational System Metrics")
col1, col2, col3, col4 = st.columns(4)

if total_impacted > 0:
    success_rate = round((total_assigned / total_impacted) * 100, 2)
    direct_count = len(df_assigned[df_assigned['type'] == 'direct'])
    multi_count = len(df_assigned[df_assigned['type'] == 'multi_hop'])
else:
    success_rate = 0.0
    direct_count, multi_count = 0, 0

col1.metric("Total Impacted", total_impacted)
col2.metric("Successfully Assigned", total_assigned)
col3.metric("Exceptions (Unassigned List)", total_exceptions)
col4.metric("Engine Success Rate", f"{success_rate}%")

# Main Content Layout Tabs 
tab1, tab2, tab3 = st.tabs(["📋 Assigned Routes", "⚠️ Exception Roster", "🔍 Search Passenger"])

with tab1:
    st.subheader("Successful Flight Level & PNR Re-accommodations")
    if not df_assigned.empty:
        st.dataframe(df_assigned, use_container_width=True)
    else:
        st.info("No assignment data available.")

with tab2:
    st.subheader("PNR Level Exceptions (No Majority Categories/Paths Found)")
    if not df_exceptions.empty:
        st.dataframe(df_exceptions, use_container_width=True)
    else:
        st.success("Zero passengers currently in exceptions list.")

with tab3:
    st.subheader("Search Passenger")
    pnr_input = st.text_input("Enter Unique PNR ID to track status:")
    if pnr_input:
        match_assigned = df_assigned[df_assigned['pnr_id'] == pnr_input]
        match_exception = df_exceptions[df_exceptions['pnr_id'] == pnr_input]
        
        if not match_assigned.empty:
            row = match_assigned.iloc[0]
            st.success("Passenger successfully re-routed.")
            st.write("PNR ID:", row['pnr_id'])
            st.write("Passenger ID:", row['passenger_id'])
            st.write("Old Flight:", row['old_flight'])
            st.write("New Flight:", row['new_flight'])
            st.write("Type:", row['type'])
            st.write("Reason:", row['reason'])
        elif not match_exception.empty:
            st.error("Passenger listed in current system exceptions roster.")
            st.dataframe(match_exception)
        else:
            st.warning("PNR sequence not found inside current runtime tracks.")