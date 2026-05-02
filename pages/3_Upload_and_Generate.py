import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import sqlite3
import pandas as pd
from core.generator.pipeline import process_and_store_documents
from core.ui import apply_theme, page_header

st.set_page_config(page_title="Upload & Sort - AEGIS-MIND", layout="wide")
apply_theme()

page_header(
    "Upload & Sort Material",
    "Upload PDFs and let local AI organize your notes into the syllabus topics you already mapped.",
    "Document intelligence",
)

# Fetch available subjects
@st.cache_data
def get_subjects():
    try:
        conn = sqlite3.connect("student_helper.db")
        df = pd.read_sql_query("SELECT DISTINCT Subject_Name FROM Syllabus_Topics ORDER BY Subject_Name", conn)
        conn.close()
        return df["Subject_Name"].tolist()
    except Exception:
        return []

subjects = get_subjects()

if not subjects:
    st.info("No syllabus data found. Please go to 'Syllabus Mapping' to add a subject first.")
    st.stop()

# Section 1 - Subject Selection
st.header("1. Select Subject")
selected_subject = st.selectbox("Which subject are these materials for?", subjects)

# Section 2 - Multiple PDF Upload
st.header("2. Upload Documents")
uploaded_files = st.file_uploader("Upload your notes/slides (PDF)", type=["pdf"], accept_multiple_files=True)

# Section 3 - Process Button
if st.button("Process & Sort Documents", type="primary"):
    if not uploaded_files:
        st.warning("Please upload at least one PDF.")
        st.stop()
        
    temp_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "temp_uploads")
    os.makedirs(temp_dir, exist_ok=True)
    
    saved_paths = []
    for file in uploaded_files:
        path = os.path.join(temp_dir, file.name)
        with open(path, "wb") as f:
            f.write(file.getbuffer())
        saved_paths.append(path)
        
    with st.spinner(f"Processing {len(saved_paths)} document(s). The first run will download an 80MB local AI model. Please be patient..."):
        try:
            summary = process_and_store_documents(saved_paths, selected_subject)
            st.success("Documents successfully processed, sorted, and stored!")
            
            st.subheader("Classification Summary")
            # Convert summary to dataframe for nice display
            df_summary = pd.DataFrame(list(summary.items()), columns=["Topic", "Chunks Extracted"])
            st.dataframe(df_summary, use_container_width=True)
            
        except Exception as e:
            st.error(f"Failed during processing: {str(e)}")
            
    # Cleanup temp files
    for path in saved_paths:
        try:
            os.remove(path)
        except:
            pass
