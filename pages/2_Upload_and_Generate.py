import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import time
from phase3.pipeline import run_pipeline
from phase4.question_store import store_questions
from phase4.session_logger import create_session

st.set_page_config(page_title="Upload & Generate - AEGIS-MIND", layout="wide")

student_id = st.session_state.get("student_id", 1)

st.title("Upload Material & Generate Test")

# Section 1 - Pre-Session Vitals
st.header("Pre-Session Vitals")
sleep_hours = st.slider("How many hours did you sleep?", 0.0, 12.0, 7.0, step=0.5)
stress_level = st.slider("Current stress level", 1, 10, 5)

st.session_state["sleep_hours"] = sleep_hours
st.session_state["stress_level"] = stress_level

# Section 2 - PDF Upload
st.header("Upload Document")
uploaded_file = st.file_uploader("Upload your notes PDF", type=["pdf"])
topic_tag = st.text_input("Topic Tag (e.g. Electrostatics)")

# Section 3 - Generate Button
if st.button("Generate Questions"):
    if not uploaded_file:
        st.warning("Please upload a PDF.")
        st.stop()
    if not topic_tag:
        st.warning("Please enter a Topic Tag.")
        st.stop()
        
    pdf_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "temp_uploaded.pdf")
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    test_id = int(time.time())
    st.session_state["current_test_id"] = test_id
    st.session_state["current_topic"] = topic_tag
    
    with st.spinner("Initializing session..."):
        create_session(student_id, test_id, sleep_hours, stress_level)
    
    with st.spinner("Analyzing PDF and generating questions via Gemini..."):
        try:
            questions = run_pipeline(pdf_path, topic_tag)
        except Exception as e:
            st.error(f"Failed during generation: {str(e)}")
            st.stop()
            
    with st.spinner("Storing questions into database..."):
        store_questions(questions, student_id, test_id, topic_tag)
        st.session_state["questions_ready"] = True
        
    st.success(f"5 questions generated for {topic_tag}. Head to Take Test to begin.")
    
if st.session_state.get("questions_ready"):
    if st.button("Go to Test →"):
        st.switch_page("pages/3_Take_Test.py")
