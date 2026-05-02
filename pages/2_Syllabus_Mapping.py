import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import sqlite3
import pandas as pd
from core.syllabus.syllabus_parser import parse_unit_text, store_syllabus, load_syllabus_edges
from core.ui import apply_theme, page_header, divider

st.set_page_config(page_title="Syllabus Mapping - AEGIS-MIND", layout="wide")
apply_theme()

page_header(
    "Syllabus Mapping",
    "Paste your syllabus content and build a clean prerequisite graph from the order of your units and topics.",
    "Knowledge structure",
)

# ─── Section 1: Input Form ────────────────────────────────────────────────────

st.header("Enter Syllabus Details")

subject_name = st.text_input(
    "Subject Name",
    placeholder="e.g. Mathematics for Intelligent Systems"
)

num_units = st.number_input(
    "Number of Units",
    min_value=1,
    max_value=12,
    value=1,
    step=1
)

divider()
st.subheader("Paste Unit Content")
st.caption(
    "Copy the syllabus text for each unit below. "
    "Topics separated by dashes ( - or \u2013 ) will be automatically detected."
)

unit_texts = {}
for i in range(1, int(num_units) + 1):
    unit_texts[i] = st.text_area(
        f"Unit {i}",
        height=120,
        placeholder=(
            "e.g. Gaussian elimination \u2013 LU decomposition \u2013 "
            "Vector spaces \u2013 QR decomposition \u2013 Gram-Schmidt ..."
        ),
        key=f"unit_{i}_text"
    )

# ─── Section 2: Preview Before Saving ─────────────────────────────────────────

if st.button("Preview Parsed Topics"):
    if not subject_name.strip():
        st.warning("Please enter a subject name.")
        st.stop()

    has_content = False
    for i in range(1, int(num_units) + 1):
        raw = unit_texts[i].strip()
        if not raw:
            continue
        has_content = True
        topics = parse_unit_text(raw)
        st.markdown(f"**Unit {i}** \u2014 {len(topics)} topics detected:")
        for idx, t in enumerate(topics, 1):
            st.markdown(f"&emsp;{idx}. {t}")
        # Show prerequisite chain
        if len(topics) > 1:
            chain = " \u2192 ".join(topics)
            st.caption(f"Prerequisite chain: {chain}")

    if not has_content:
        st.warning("Please paste syllabus content for at least one unit.")

# ─── Section 3: Save to Database ──────────────────────────────────────────────

divider()
if st.button("Save Syllabus Mapping", type="primary"):
    if not subject_name.strip():
        st.warning("Please enter a subject name.")
        st.stop()

    parsed_units = {}
    for i in range(1, int(num_units) + 1):
        raw = unit_texts[i].strip()
        if raw:
            parsed_units[i] = parse_unit_text(raw)

    if not parsed_units:
        st.warning("No unit content to save. Paste at least one unit's syllabus.")
        st.stop()

    total = store_syllabus(subject_name.strip(), parsed_units)
    st.success(f"Saved {total} topics across {len(parsed_units)} unit(s) for **{subject_name}**.")

    # Verification: read back from DB
    conn = sqlite3.connect("student_helper.db")
    verify_df = pd.read_sql_query(
        "SELECT Unit_Number, Topic_Order, Topic_Name FROM Syllabus_Topics "
        "WHERE Subject_Name = ? ORDER BY Unit_Number, Topic_Order",
        conn, params=(subject_name.strip(),)
    )
    conn.close()

    if not verify_df.empty:
        st.subheader("Stored Topics (DB Verification)")
        verify_df.rename(columns={
            "Unit_Number": "Unit",
            "Topic_Order": "Order",
            "Topic_Name": "Topic"
        }, inplace=True)
        st.dataframe(verify_df, use_container_width=True)

    # Show derived edges
    edges = load_syllabus_edges()
    if edges:
        st.subheader("Derived Prerequisite Edges")
        for prereq, target in edges:
            st.markdown(f"- **{prereq}** \u2192 {target}")

# ─── Section 4: Current Syllabus Data ─────────────────────────────────────────

divider()
st.header("Currently Stored Syllabi")

conn = sqlite3.connect("student_helper.db")
try:
    existing = pd.read_sql_query(
        "SELECT DISTINCT Subject_Name FROM Syllabus_Topics ORDER BY Subject_Name",
        conn
    )
except Exception:
    existing = pd.DataFrame()
conn.close()

if existing.empty:
    st.info("No syllabus data stored yet. Use the form above to add one.")
else:
    for _, row in existing.iterrows():
        subj = row["Subject_Name"]
        conn = sqlite3.connect("student_helper.db")
        subj_df = pd.read_sql_query(
            "SELECT Unit_Number, Topic_Order, Topic_Name FROM Syllabus_Topics "
            "WHERE Subject_Name = ? ORDER BY Unit_Number, Topic_Order",
            conn, params=(subj,)
        )
        conn.close()

        with st.expander(f"{subj} ({len(subj_df)} topics)"):
            subj_df.rename(columns={
                "Unit_Number": "Unit",
                "Topic_Order": "Order",
                "Topic_Name": "Topic"
            }, inplace=True)
            st.dataframe(subj_df, use_container_width=True)
