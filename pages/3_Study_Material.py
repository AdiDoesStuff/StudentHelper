import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import sqlite3
import pandas as pd
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

st.set_page_config(page_title="Study Material - AEGIS-MIND", layout="wide")

st.title("📚 Study Material")
st.markdown("Review the study material you've uploaded, organized by topic.")

# --- Database Fetching ---
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
        # Adding the Uncategorized option just in case they want to review unmatched chunks
        topics_with_uncat = topics + ["Uncategorized"]
        selected_topic = st.selectbox("Select Topic", topics_with_uncat)
    else:
        selected_topic = None

# --- Retrieval & Display ---
if selected_subject and selected_topic:
    st.markdown("---")
    st.subheader(f"Material for: {selected_topic}")
    
    with st.spinner("Fetching material from database..."):
        try:
            embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            vectorstore = Chroma(
                collection_name="student_helper_rag",
                embedding_function=embeddings,
                persist_directory="./chroma_db"
            )
            
            # Query chroma for exact match on Topic_Tag
            results = vectorstore.get(where={"Topic_Tag": selected_topic})
            
            docs = results.get("documents", [])
            metadatas = results.get("metadatas", [])
            
            if not docs:
                st.info("No material has been uploaded and sorted into this topic yet.")
            else:
                st.success(f"Found {len(docs)} text chunks for this topic.")
                
                # Zip and prepare for display
                chunk_data = [{"text": d, "page": m.get("page", "Unknown")} for d, m in zip(docs, metadatas)]
                
                # Display chunks
                for i, chunk in enumerate(chunk_data):
                    with st.container(border=True):
                        st.caption(f"Chunk {i+1} | Source Page: {chunk['page']}")
                        st.markdown(chunk["text"])
                        
        except Exception as e:
            st.error(f"Error connecting to the database. Make sure you have uploaded files first. Details: {e}")
