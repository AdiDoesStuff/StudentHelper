import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

from core.analytics.kurtosis_analysis import analyze_kurtosis
from core.analytics.knowledge_graph import build_knowledge_graph, get_root_causes
from core.analytics.diagnostics import get_student_correlation

st.set_page_config(page_title="Diagnostic Report - AEGIS-MIND", layout="wide")

student_id = st.session_state.get("student_id", 1)

st.title("Full Diagnostic Report")

conn = sqlite3.connect("student_helper.db")
query = """
    SELECT sp.*, st.Subject_Name 
    FROM Student_Profile sp
    LEFT JOIN Syllabus_Topics st ON sp.Topic_Tag = st.Topic_Name
    WHERE sp.Student_ID = ? 
    ORDER BY st.Subject_Name ASC, sp.Weakness_Index DESC
"""
profile_df = pd.read_sql_query(query, conn, params=(student_id,))

# Section 1 - Weakness Index Rankings
st.header("Weakness Index Rankings")
if profile_df.empty:
    st.info("No data available.")
else:
    profile_df["Subject_Name"] = profile_df["Subject_Name"].fillna("Other / Uncategorized")
    
    subjects = profile_df["Subject_Name"].unique()
    for subject in subjects:
        st.subheader(f"📚 {subject}")
        subject_df = profile_df[profile_df["Subject_Name"] == subject]
        
        for _, row in subject_df.iterrows():
            topic = row["Topic_Tag"]
            wk_idx = row["Weakness_Index"]
            
            if wk_idx > 0.6:
                color = "🔴"
            elif wk_idx > 0.3:
                color = "🟠"
            else:
                color = "🟢"
                
            st.markdown(f"&nbsp;&nbsp; {color} **{topic}** (Index: {wk_idx:.2f})")

# Section 2 - Kurtosis Diagnosis Per Topic
st.header("Kurtosis Diagnosis")
kurtosis_results = analyze_kurtosis()

has_kurtosis = False
diag_map = {
    "Specific Block": "You struggle on one particular question type in this topic.",
    "General Weakness": "Broad remediation is needed across all sub-concepts in this topic.",
    "Insufficient Data": "Not enough attempts to accurately diagnose a pattern."
}

if kurtosis_results:
    has_kurtosis = True
    for topic, data in kurtosis_results.items():
        label = data.get("Label", "N/A")
        kv = data.get("Kurtosis")
        interpretation = diag_map.get(label, "Unknown")
        st.markdown(f"**{topic}**: {label}")
        kv_display = f"{kv:.2f}" if kv is not None else "N/A"
        st.caption(f"{interpretation} (Kurtosis: {kv_display})")
                
if not has_kurtosis:
    st.info("No sufficient kurtosis data to display for your topics.")

# Section 3 - Environmental Correlation
st.header("Environmental Correlation")
correlations = get_student_correlation(student_id)

if correlations:
    sleep_data = correlations.get("Sleep", {})
    stress_data = correlations.get("Stress", {})
    sleep_r = sleep_data.get("r", 0.0)
    stress_r = stress_data.get("r", 0.0)
    
    col1, col2 = st.columns(2)
    col1.metric("Sleep vs Accuracy", f"r = {sleep_r:.2f}", delta=sleep_r)
    col2.metric("Stress vs Accuracy", f"r = {stress_r:.2f}", delta=stress_r)
    
    st.markdown("""
        **Interpretation**:
        - A positive correlation means your performance drops when that factor decreases (e.g. less sleep = worse score).
        - A negative correlation means your performance drops when that factor increases (e.g. more stress = worse score).
    """)
else:
    st.info("Not enough data to calculate correlations (minimum 3 sessions required).")

# Section 4 - Knowledge Graph Root Causes
st.header("Knowledge Graph Root Causes")
G = build_knowledge_graph()

has_weakness = False
for _, row in profile_df.iterrows():
    if row["Weakness_Index"] > 0.5:
        has_weakness = True
        topic = row["Topic_Tag"]
        roots = get_root_causes(G, topic)
        with st.expander(f"Review Prerequisites for: {topic}"):
            if roots:
                st.markdown("You should review the following prerequisite topics:")
                for r in roots:
                    st.markdown(f"- **{r}**")
            else:
                st.markdown("No earlier prerequisites identified for this topic. Focus directly on it.")

if not has_weakness:
    st.success("No heavy weaknesses (>0.5) currently detected needing root cause extraction.")

# Section 5 - Performance History Chart
st.header("Performance History")
query = """
    SELECT a.Test_ID, b.Session_Date, AVG(
        CAST(a.Outcome AS FLOAT)
    ) as Session_Accuracy
    FROM Academic_Performance_Log a
    JOIN Behavioural_Log b ON a.Test_ID = b.Test_ID
    WHERE a.Student_ID = ?
    GROUP BY a.Test_ID, b.Session_Date
    ORDER BY b.Session_Date ASC
"""
history_df = pd.read_sql_query(query, conn, params=(student_id,))
conn.close()

if not history_df.empty:
    # Convert accuracy to percentage
    history_df["Accuracy %"] = history_df["Session_Accuracy"] * 100
    fig = px.line(history_df, x="Session_Date", y="Accuracy %", markers=True, title="Accuracy Over Time")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No performance history to plot.")
