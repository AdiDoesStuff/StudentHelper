import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from core.analytics.planner import generate_study_plan, _get_upcoming_test_instances
from core.ui import apply_theme, page_header, divider

st.set_page_config(page_title="Study Planner", page_icon="📅", layout="wide")
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

def delete_test_schedule(schedule_id, subject_name, day_of_week):
    conn = get_db_connection()
    # Delete the recurring template
    conn.execute("DELETE FROM Weekly_Test_Schedule WHERE Schedule_ID = ?", (schedule_id,))
    # Delete any future unimported instances for this subject on this day to clean the calendar
    today_str = datetime.now().strftime("%Y-%m-%d")
    # We find instances matching subject, >= today, and not imported.
    # We could filter by day_of_week exactly, but SQLite doesn't have a built-in day_of_week name function easily.
    # Deleting all unimported future instances of that subject is generally safe here.
    conn.execute("""
        DELETE FROM Test_Instances 
        WHERE Student_ID = ? AND Subject_Name = ? AND Test_Date >= ? AND Is_Imported = 0
    """, (student_id, subject_name, today_str))
    conn.commit()
    conn.close()
    st.rerun()

page_header(
    "Personalized Study Planner",
    "Connect recurring tests, upcoming calendar pressure, weak areas, and availability into an actionable study plan.",
    "Plan the next move",
)

student_id = get_student_id()
if not student_id:
    st.warning("No student found in database. Please configure a student first.")
    st.stop()

# --- Weekly Test Schedule (Main Page) ---
st.subheader("📚 Weekly Test Schedule")
st.write("Add recurring tests here. They will automatically populate in your calendar below.")

with st.expander("➕ Add New Test Schedule", expanded=False):
    with st.form("add_test_schedule_form"):
        conn = get_db_connection()
        subjects_df = pd.read_sql_query("SELECT DISTINCT Subject_Name FROM Syllabus_Topics", conn)
        conn.close()
        subject_list = subjects_df["Subject_Name"].tolist() if not subjects_df.empty else ["No Subjects Found"]
        
        col1, col2 = st.columns(2)
        with col1:
            test_subject = st.selectbox("Subject", subject_list)
        with col2:
            test_day = st.selectbox("Test Day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
            
        submitted = st.form_submit_button("Add Test Schedule")
        if submitted:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 1 FROM Weekly_Test_Schedule 
                WHERE Student_ID=? AND Subject_Name=? AND Day_of_Week=?
            """, (student_id, test_subject, test_day))
            if not cursor.fetchone():
                conn.execute("INSERT INTO Weekly_Test_Schedule (Student_ID, Subject_Name, Day_of_Week) VALUES (?, ?, ?)",
                             (student_id, test_subject, test_day))
                conn.commit()
                st.success(f"Added recurring test for {test_subject} on {test_day}s")
                st.rerun()
            else:
                st.info("Test schedule already exists.")
            conn.close()

conn = get_db_connection()
schedules_df = pd.read_sql_query(
    "SELECT Schedule_ID, Subject_Name, Day_of_Week FROM Weekly_Test_Schedule WHERE Student_ID = ?", 
    conn, params=(student_id,)
)
conn.close()

if not schedules_df.empty:
    h1, h2, h3 = st.columns([3, 3, 2])
    h1.markdown("**Subject**")
    h2.markdown("**Test Day**")
    h3.markdown("**Action**")
    st.markdown("<hr style='margin:0.5em 0;'>", unsafe_allow_html=True)
    
    for idx, row in schedules_df.iterrows():
        c1, c2, c3 = st.columns([3, 3, 2])
        c1.write(row['Subject_Name'])
        c2.write(row['Day_of_Week'])
        if c3.button("Delete", key=f"del_ts_{row['Schedule_ID']}"):
            delete_test_schedule(row['Schedule_ID'], row['Subject_Name'], row['Day_of_Week'])
else:
    st.info("No recurring tests configured.")

divider()

# --- Calendar View (Native) ---
st.subheader("🗓️ Next 14 Days")
st.write("Your upcoming tests. Toggle the checkbox if you have taken the test and imported it into the system via Evalify.")

conn = get_db_connection()
# Ensure instances are generated for next 14 days
_get_upcoming_test_instances(student_id, datetime.now(), 14)

upcoming_tests = pd.read_sql_query(
    "SELECT Instance_ID, Subject_Name, Test_Date, Is_Imported FROM Test_Instances WHERE Student_ID = ? AND Test_Date >= ? ORDER BY Test_Date ASC LIMIT 30",
    conn, params=(student_id, datetime.now().strftime("%Y-%m-%d"))
)

def update_import_status(instance_id, current_status):
    new_status = 1 if current_status == 0 else 0
    c = get_db_connection()
    c.execute("UPDATE Test_Instances SET Is_Imported = ? WHERE Instance_ID = ?", (new_status, instance_id))
    c.commit()
    c.close()

if not upcoming_tests.empty:
    cols = st.columns(7)
    today = datetime.now().date()
    
    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    for i, day_name in enumerate(days_order):
        with cols[i]:
            st.markdown(f"**{day_name}**")
            
            day_tests = upcoming_tests[upcoming_tests['Test_Date'].apply(lambda x: datetime.strptime(x, "%Y-%m-%d").strftime("%A")) == day_name]
            
            for _, row in day_tests.iterrows():
                date_str = row['Test_Date']
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                is_past = date_obj < today
                color = "#2e7d32" if row["Is_Imported"] else ("#d32f2f" if is_past else "#1976d2")
                
                st.markdown(f"*{date_str}*")
                st.markdown(f"<div style='padding:5px; border-radius:5px; background-color:{color}; color:white; font-size:12px; margin-bottom:5px; text-align:center;'>{row['Subject_Name']}</div>", unsafe_allow_html=True)
                
                checked = bool(row["Is_Imported"])
                st.checkbox("Imported", value=checked, key=f"chk_{row['Instance_ID']}", 
                            on_change=update_import_status, args=(row['Instance_ID'], row['Is_Imported']))
else:
    st.info("No upcoming tests scheduled.")

conn.close()

divider()

# --- Study Plan View ---
colA, colB = st.columns([3, 1])
with colA:
    st.subheader("📖 Actionable Study Plan")
with colB:
    if st.button("Force Regenerate Plan", type="primary"):
        st.session_state["force_regen"] = True

force_regen = st.session_state.get("force_regen", False)
if force_regen:
    st.session_state["force_regen"] = False

with st.spinner("Generating / Loading Study Plan..."):
    try:
        plan = generate_study_plan(student_id, force_regenerate=force_regen)
        if "error" in plan:
            st.warning(plan["error"])
        elif "study_plan_markdown" in plan:
            st.markdown(plan["study_plan_markdown"])
        else:
            st.error("Unexpected plan format.")
    except Exception as e:
        st.error(f"Error generating study plan: {e}")
