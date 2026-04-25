import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import time, datetime, io, contextlib
import sqlite3, json

from core.runner.session_logger import log_answers
from core.analytics.preprocessing import PreprocessingPipeline
from core.analytics.diagnostics import run_diagnostics

st.set_page_config(page_title="Take Test - AEGIS-MIND", layout="wide")

student_id = st.session_state.get("student_id", 1)

if not st.session_state.get("questions_ready"):
    st.warning("No test is ready. Please upload a PDF on the Upload page first.")
    st.stop()

# Initialize State Variables
if "current_question_index" not in st.session_state:
    st.session_state["current_question_index"] = 0

if "test_answers" not in st.session_state:
    st.session_state["test_answers"] = []

if "question_start_time" not in st.session_state:
    st.session_state["question_start_time"] = time.time()

if "test_complete" not in st.session_state:
    st.session_state["test_complete"] = False

test_id = st.session_state.get("current_test_id")
# topic_tag is now fetched per-question

# Load Questions
if "loaded_questions" not in st.session_state:
    conn = sqlite3.connect("student_helper.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Question_ID, Question_Text, Options, Correct_Answer, Difficulty_Level, Topic_Tag
        FROM Questions 
        WHERE Test_ID = ? AND Was_Asked = 0 
        ORDER BY Question_ID ASC
    """, (test_id,))
    rows = cursor.fetchall()
    conn.close()
    
    questions = []
    for r in rows:
        questions.append({
            "Question_ID": r[0],
            "Question_Text": r[1],
            "options": json.loads(r[2]),
            "Correct_Answer": r[3],
            "Difficulty_Level": r[4],
            "Topic_Tag": r[5]
        })
    st.session_state["loaded_questions"] = questions

questions = st.session_state["loaded_questions"]
total_questions = len(questions)

if total_questions == 0:
    st.warning("No unasked questions found for this test. Maybe you already completed it?")
    if st.button("Start New Session"):
        st.session_state.clear()
        st.switch_page("pages/4_Generate_Test.py")
    st.stop()

if not st.session_state["test_complete"]:
    current_index = st.session_state["current_question_index"]
    
    st.progress(current_index / total_questions)
    st.subheader(f"Question {current_index + 1} of {total_questions}")
    
    q_data = questions[current_index]
    
    with st.container():
        st.markdown(f"**{q_data['Question_Text']}**")
        
        # User answer selection
        with st.form("question_form"):
            selected = st.radio("Select your answer:", q_data["options"], index=None)
            submitted = st.form_submit_button("Submit Answer")
            
            if submitted:
                if not selected:
                    st.warning("Please select an answer.")
                else:
                    time_spent = time.time() - st.session_state["question_start_time"]
                    time_of_day = datetime.datetime.now().strftime("%H:%M")
                    
                    student_ans = selected[0] # Extract letter
                    correct_ans = q_data['Correct_Answer']
                    outcome = 1 if student_ans == correct_ans else 0
                    
                    st.session_state["test_answers"].append({
                        "student_id": student_id,
                        "test_id": test_id,
                        "topic_tag": q_data["Topic_Tag"],
                        "question_id": q_data["Question_ID"],
                        "outcome": outcome,
                        "time_spent_seconds": time_spent,
                        "difficulty_level": q_data["Difficulty_Level"],
                        "test_sequence_number": current_index + 1,
                        "student_answer": student_ans,
                        "correct_answer": correct_ans,
                        "time_of_day": time_of_day
                    })
                    
                    # Update Was_Asked
                    conn = sqlite3.connect("student_helper.db")
                    conn.execute("UPDATE Questions SET Was_Asked = 1 WHERE Question_ID = ?", (q_data["Question_ID"],))
                    conn.commit()
                    conn.close()
                    
                    st.session_state["current_question_index"] += 1
                    st.session_state["question_start_time"] = time.time()
                    
                    if st.session_state["current_question_index"] >= total_questions:
                        st.session_state["test_complete"] = True
                    
                    st.rerun()
else:
    # Test Complete Screen
    st.title("Test Complete")
    
    with st.spinner("Processing results and updating diagnostic profile..."):
        # Log Answers
        if "results_logged" not in st.session_state:
            log_answers(st.session_state["test_answers"])
            PreprocessingPipeline().run()
            
            # Run diagnostics and capture output
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                run_diagnostics(student_id)
            diag_output = buffer.getvalue()
            
            st.session_state["diag_output"] = diag_output
            st.session_state["results_logged"] = True
    
    ans = st.session_state["test_answers"]
    correct = sum(1 for a in ans if a["outcome"] == 1)
    total = len(ans)
    
    st.metric("Your Score", f"{correct}/{total}")
    
    # Results breakdown table
    import pandas as pd
    res_df = pd.DataFrame(ans)
    
    def format_outcome(o):
        return "✅" if o == 1 else "❌"
        
    display_res = pd.DataFrame({
        "Question": range(1, total + 1),
        "Your Answer": res_df["student_answer"],
        "Correct Answer": res_df["correct_answer"],
        "Outcome": res_df["outcome"].apply(format_outcome),
        "Time (s)": res_df["time_spent_seconds"].round(1)
    })
    st.table(display_res)
    
    st.success("Your diagnostic profile has been updated!")
    
    with st.expander("View Diagnostic Process Log"):
        st.text(st.session_state["diag_output"])
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("View Diagnostic Report →"):
            st.switch_page("pages/6_Diagnostic_Report.py")
    with col2:
        if st.button("Start New Session"):
            st.session_state.clear()
            st.switch_page("pages/4_Generate_Test.py")
