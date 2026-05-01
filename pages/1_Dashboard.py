import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from core.runner.agent import get_weakest_topic

st.set_page_config(page_title="Dashboard - AEGIS-MIND", layout="wide")

student_id = st.session_state.get("student_id", 1)

st.title("Student Dashboard")

conn = sqlite3.connect("student_helper.db")
profile_df = pd.read_sql_query(
    "SELECT * FROM Student_Profile WHERE Student_ID = ? ORDER BY Weakness_Index DESC",
    conn, params=(student_id,)
)
conn.close()

# Section 1 - Recommended Focus Topic
st.header("Recommended Focus Topic")
recommended = get_weakest_topic(student_id)

if recommended:
    wk_index_row = profile_df[profile_df["Topic_Tag"] == recommended]
    wk_index = wk_index_row["Weakness_Index"].iloc[0] if not wk_index_row.empty else 0.0
    st.info(f"**Focus Area:** {recommended}\n\n"
            f"**Weakness Index:** {wk_index:.2f}\n\n"
            f"This topic has the highest weighted failure rate and hasn't been tested recently.")
else:
    st.success("You're all caught up! No specific weakness identified.")


if profile_df.empty:
    st.warning("No data found for this student.")
    st.stop()

# Format Accuracy
profile_df["Average_Accuracy_Pct"] = (profile_df["Average_Accuracy"] * 100).round(1).astype(str) + "%"

# Section 2 - Topic Weakness Overview (Bar Chart)
st.header("Topic Weakness Overview")
def color_rule(val):
    if val > 0.6: return "High (>0.6)"
    if val > 0.3: return "Medium (0.3-0.6)"
    return "Low (<0.3)"

profile_df["Severity"] = profile_df["Weakness_Index"].apply(color_rule)
color_map = {"High (>0.6)": "red", "Medium (0.3-0.6)": "orange", "Low (<0.3)": "green"}

fig = px.bar(
    profile_df, 
    x="Weakness_Index", 
    y="Topic_Tag", 
    orientation='h',
    color="Severity",
    color_discrete_map=color_map,
    title="Weakness by Topic (Higher is worse)"
)
fig.update_layout(yaxis={'categoryorder':'total ascending'})
st.plotly_chart(fig, use_container_width=True)

# Section 3 - Topic Detail Table
st.header("Detailed Topic Metrics")
display_df = profile_df[["Topic_Tag", "Weakness_Index", "Average_Accuracy_Pct", "Last_Tested_Date", "Total_Sessions"]].copy()
display_df.rename(columns={
    "Topic_Tag": "Topic", 
    "Weakness_Index": "Weakness Index",
    "Average_Accuracy_Pct": "Accuracy",
    "Last_Tested_Date": "Last Tested",
    "Total_Sessions": "Total Sessions"
}, inplace=True)
display_df["Last Tested"] = display_df["Last Tested"].fillna("Never tested")

st.dataframe(display_df, use_container_width=True)

# Section 4 - Session Stats
st.header("Overall Session Stats")

conn = sqlite3.connect("student_helper.db")
# Fetch accurate counts directly from raw logs
total_sessions = pd.read_sql_query(
    "SELECT COUNT(*) FROM Behavioural_Log WHERE Student_ID = ?", 
    conn, params=(student_id,)
).iloc[0, 0]

overall_acc = pd.read_sql_query(
    "SELECT AVG(Outcome) FROM Academic_Performance_Log WHERE Student_ID = ?", 
    conn, params=(student_id,)
).iloc[0, 0]

latest_date_str = pd.read_sql_query(
    "SELECT MAX(Session_Date) FROM Behavioural_Log WHERE Student_ID = ?", 
    conn, params=(student_id,)
).iloc[0, 0]
conn.close()

# Days since last test math
if not latest_date_str:
    days_since_str = "N/A"
else:
    try:
        latest_date = pd.to_datetime(latest_date_str)
        days_since = (pd.Timestamp.now() - latest_date).days
        days_since_str = str(days_since)
    except Exception:
        days_since_str = "Error parsing date"

col1, col2, col3 = st.columns(3)
col1.metric("Total Sessions", int(total_sessions))
col2.metric("Overall Average Accuracy", f"{overall_acc*100:.1f}%" if pd.notnull(overall_acc) else "0%")
col3.metric("Days Since Last Test", days_since_str)
