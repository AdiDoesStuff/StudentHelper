import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import sqlite3
import pandas as pd
from core.generator.test_builder import build_test

st.set_page_config(page_title="Generate Test - AEGIS-MIND", layout="wide")

st.title("🎯 Generate Test")
st.markdown("Create a customized MCQ test based on your study materials.")

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
        selected_topics = st.multiselect("Select Topics (One or Multiple)", topics)
    else:
        selected_topics = []

st.markdown("---")
st.subheader("Test Configuration")

col3, col4, col5 = st.columns(3)

with col3:
    num_questions = st.number_input("Number of Questions", min_value=1, max_value=20, value=5, step=1)

with col4:
    sleep_hours = st.number_input("Hours Slept Last Night", min_value=0.0, max_value=24.0, value=7.0, step=0.5, help="Used for behavioural analysis.")

with col5:
    stress_level = st.slider("Current Stress Level (1-10)", min_value=1, max_value=10, value=5, help="1 = Very Relaxed, 10 = Very Stressed.")

st.markdown("---")
st.subheader("AI Provider")

AI_PROVIDERS = ["Gemini", "Groq (Llama 3.3 70B)"]
ai_provider = st.radio(
    "Choose the AI model to generate your questions:",
    AI_PROVIDERS,
    horizontal=True,
    help="Gemini uses Google's Gemini 2.5 Flash Lite. Groq uses Meta's Llama 3.3 70B via Groq's fast inference API."
)

if st.button("Generate Test", type="primary"):
    if not selected_topics:
        st.warning("Please select at least one topic.")
        st.stop()
        
    student_id = st.session_state.get("student_id", 1)
        
    with st.spinner(f"Retrieving study materials and generating {num_questions} questions using {ai_provider}. This may take a minute..."):
        try:
            test_id = build_test(
                student_id=student_id,
                subject=selected_subject,
                topics=selected_topics,
                num_questions=num_questions,
                sleep_hours=sleep_hours,
                stress_level=stress_level,
                ai_provider=ai_provider
            )
            
            # Setup session state for the Take Test page
            st.session_state["questions_ready"] = True
            st.session_state["current_test_id"] = test_id
            # Note: We don't set "current_topic" anymore as questions come from multiple topics
            
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
            
            st.success("Test Generated Successfully!")
            st.page_link("pages/6_Take_Test.py", label="Take Test Now", icon="📝")
            
        except Exception as e:
            st.error(f"Error generating test: {e}")
