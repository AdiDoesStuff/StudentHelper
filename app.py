import streamlit as st
from database_init import init_db
import sqlite3

st.set_page_config(page_title="AEGIS-MIND", layout="wide")

init_db()  # Safe to call repeatedly — uses CREATE IF NOT EXISTS

# Sidebar: removed user selection dropdown for Single-Student design.
st.session_state["student_id"] = 1

# Home screen content
st.title("AEGIS-MIND")
st.markdown("AI-powered adaptive learning diagnostics.")
