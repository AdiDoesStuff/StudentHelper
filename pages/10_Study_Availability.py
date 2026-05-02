import streamlit as st
import sqlite3
import pandas as pd
from core.ui import apply_theme, page_header, divider

st.set_page_config(page_title="Study Availability", page_icon="🕒", layout="wide")
apply_theme()

DB_PATH = "student_helper.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_student_id():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Student_ID FROM Students LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    if row:
        return row["Student_ID"]
    return None

page_header(
    "Study Availability",
    "Set the weekly hours you can realistically study so your planner stays useful, not imaginary.",
    "Time setup",
)

student_id = get_student_id()
if not student_id:
    st.warning("No student found in database. Please configure a student first.")
    st.stop()

def delete_availability(availability_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM Study_Availability WHERE Availability_ID = ?", (availability_id,))
    conn.commit()
    conn.close()
    st.rerun()

st.subheader("Add New Slot")
with st.form("add_availability_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        day = st.selectbox("Day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
    with col2:
        start_time = st.time_input("Start Time")
    with col3:
        end_time = st.time_input("End Time")
        
    submitted = st.form_submit_button("Add Availability")
    
    if submitted:
        conn = get_db_connection()
        start_str = start_time.strftime("%H:%M")
        end_str = end_time.strftime("%H:%M")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 1 FROM Study_Availability 
            WHERE Student_ID=? AND Day_of_Week=? AND Start_Time=? AND End_Time=?
        """, (student_id, day, start_str, end_str))
        if not cursor.fetchone():
            conn.execute("INSERT INTO Study_Availability (Student_ID, Day_of_Week, Start_Time, End_Time) VALUES (?, ?, ?, ?)",
                         (student_id, day, start_str, end_str))
            conn.commit()
            st.success(f"Added {day} ({start_str} - {end_str})")
            st.rerun()
        else:
            st.warning("Availability slot already exists.")
        conn.close()

divider()
st.subheader("Your Current Availability")

conn = get_db_connection()
availability_df = pd.read_sql_query(
    "SELECT Availability_ID, Day_of_Week, Start_Time, End_Time FROM Study_Availability WHERE Student_ID = ?", 
    conn, params=(student_id,)
)
conn.close()

if not availability_df.empty:
    header_col1, header_col2, header_col3, header_col4 = st.columns([2, 2, 2, 1])
    header_col1.markdown("**Day of Week**")
    header_col2.markdown("**Start Time**")
    header_col3.markdown("**End Time**")
    header_col4.markdown("**Action**")
    
    st.markdown("<hr style='margin:0.5em 0;'>", unsafe_allow_html=True)
    
    for idx, row in availability_df.iterrows():
        col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
        col1.write(row['Day_of_Week'])
        col2.write(row['Start_Time'])
        col3.write(row['End_Time'])
        if col4.button("Delete", key=f"del_av_{row['Availability_ID']}"):
            delete_availability(row['Availability_ID'])
else:
    st.info("You haven't added any availability slots yet.")
