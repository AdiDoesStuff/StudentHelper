import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import sqlite3
import pandas as pd
from core.generator.test_builder import build_revision_test

st.set_page_config(page_title="Mistake Revision - AEGIS-MIND", layout="wide")

st.title("🔄 Mistake Revision")
st.markdown("Re-take questions you previously answered incorrectly to improve your weakness index.")

# Fetch available subjects and topics
@st.cache_data
def get_hierarchy():
    try:
        conn = sqlite3.connect("student_helper.db")
        df = pd.read_sql_query("SELECT Subject_Name, Topic_Name FROM Syllabus_Topics ORDER BY Subject_Name, Topic_Order", conn)
        conn.close()
        
        hierarchy = {}
        for _, row in df.iterrows():
            subj = row["Subject_Name"]
            topic = row["Topic_Name"]
            if subj not in hierarchy:
                hierarchy[subj] = []
            hierarchy[subj].append(topic)
        return hierarchy
    except Exception:
        return {}

hierarchy = get_hierarchy()

if not hierarchy:
    st.info("No syllabus data found. Please go to 'Syllabus Mapping' to add a subject first.")
    st.stop()

# --- Selection UI ---
col1, col2 = st.columns(2)

with col1:
    selected_subject = st.selectbox("Select Subject", list(hierarchy.keys()))

with col2:
    if selected_subject:
        topics = hierarchy[selected_subject]
        # Allow 'All Topics' by selecting all if none chosen, or explicit 'Select All'
        selected_topics = st.multiselect("Select Topics (Leave empty for All Topics)", topics)
    else:
        selected_topics = []

# If empty, use all topics in the subject
final_topics = selected_topics if selected_topics else hierarchy.get(selected_subject, [])

# Calculate available wrong questions for the selected subject and topics
student_id = st.session_state.get("student_id", 1)

def get_available_mistakes(student_id, subject, topics):
    if not topics:
        return 0
    conn = sqlite3.connect("student_helper.db")
    placeholders = ",".join(["?"] * len(topics))
    query = f"""
        SELECT COUNT(DISTINCT q.Question_Text)
        FROM Questions q
        JOIN Academic_Performance_Log a ON q.Question_ID = a.Question_ID
        JOIN Syllabus_Topics s ON q.Topic_Tag = s.Topic_Name
        WHERE a.Student_ID = ? AND a.Outcome = 0 AND s.Subject_Name = ?
        AND q.Topic_Tag IN ({placeholders})
    """
    params = [student_id, subject] + topics
    cursor = conn.cursor()
    cursor.execute(query, params)
    count = cursor.fetchone()[0]
    conn.close()
    return count

available_mistakes = get_available_mistakes(student_id, selected_subject, final_topics)

st.markdown("---")
st.subheader(f"Test Configuration (Available Mistakes: {available_mistakes})")

if available_mistakes == 0:
    st.success("Great job! You have no recorded mistakes for these topics.")
    st.stop()

col3, col4, col5 = st.columns(3)

with col3:
    num_questions = st.number_input("Number of Questions", min_value=1, max_value=available_mistakes, value=min(5, available_mistakes), step=1)

with col4:
    sleep_hours = st.number_input("Hours Slept Last Night", min_value=0.0, max_value=24.0, value=7.0, step=0.5, help="Used for behavioural analysis.")

with col5:
    stress_level = st.slider("Current Stress Level (1-10)", min_value=1, max_value=10, value=5, help="1 = Very Relaxed, 10 = Very Stressed.")

st.markdown("---")

if st.button("Generate Revision Test", type="primary"):
    with st.spinner(f"Preparing {num_questions} review questions..."):
        try:
            test_id = build_revision_test(
                student_id=student_id,
                subject=selected_subject,
                topics=final_topics,
                num_questions=num_questions,
                sleep_hours=sleep_hours,
                stress_level=stress_level
            )
            
            # Setup session state for the Take Test page
            st.session_state["questions_ready"] = True
            st.session_state["current_test_id"] = test_id
            
            # Clear out any old test state
            if "loaded_questions" in st.session_state:
                del st.session_state["loaded_questions"]
            if "test_answers" in st.session_state:
                del st.session_state["test_answers"]
            if "test_started" in st.session_state:
                del st.session_state["test_started"]
            if "question_start_time" in st.session_state:
                del st.session_state["question_start_time"]
            st.session_state["current_question_index"] = 0
            st.session_state["test_complete"] = False
            
            st.success("Revision Test Generated Successfully!")
            st.page_link("pages/6_Take_Test.py", label="Start Revision Now", icon="📝")
            
        except Exception as e:
            st.error(f"Error generating test: {e}")
