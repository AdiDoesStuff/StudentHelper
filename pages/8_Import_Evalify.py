import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import json
import sqlite3
import pandas as pd
import datetime

from core.db.database_init import migrate_db
from core.runner.evalify_importer import (
    filter_mcq_only,
    check_duplicate,
    classify_questions,
    import_evalify_test,
    _get_syllabus_topics,
)
from core.analytics.preprocessing import PreprocessingPipeline
from core.analytics.diagnostics import run_diagnostics

st.set_page_config(page_title="Import Evalify Test - AEGIS-MIND", layout="wide")

# Run migration on page load to ensure new columns exist
migrate_db()

student_id = st.session_state.get("student_id", 1)

st.title("📥 Import Evalify Test")
st.markdown(
    "Paste the JSON output from your **Evalify Tampermonkey exporter** to import "
    "an externally-taken test into your AEGIS-MIND diagnostic profile."
)

# ─── Step 1: JSON Input ───
st.header("1. Paste Exported JSON")
json_input = st.text_area(
    "Paste your Evalify JSON here",
    height=200,
    placeholder='[\n  {\n    "student_id": 1,\n    "test_id": "cmky0d...",\n    "question_text": "...",\n    ...\n  }\n]',
)

if not json_input.strip():
    st.info("Paste your JSON above to get started.")
    st.stop()

# Parse JSON
try:
    raw_data = json.loads(json_input)
    if not isinstance(raw_data, list) or len(raw_data) == 0:
        st.error("JSON must be a non-empty array of question objects.")
        st.stop()
except json.JSONDecodeError as e:
    st.error(f"Invalid JSON: {e}")
    st.stop()

# Filter MCQ only
mcq_data = filter_mcq_only(raw_data)
total_raw = len(raw_data)
total_mcq = len(mcq_data)

if total_mcq == 0:
    st.error(
        f"All {total_raw} question(s) are descriptive/coding — no MCQs to import. "
        "Only MCQ questions are supported for import."
    )
    st.stop()

if total_mcq < total_raw:
    st.warning(
        f"⚠️ {total_raw - total_mcq} descriptive/coding question(s) were filtered out. "
        f"Importing **{total_mcq} MCQ(s)** only."
    )

# ─── Duplicate check ───
external_test_id = mcq_data[0].get("test_id", "unknown")
if check_duplicate(str(external_test_id)):
    st.warning(
        f"⚠️ **Duplicate detected!** A test with External ID `{external_test_id}` "
        "has already been imported. Re-importing will create duplicate records."
    )

# ─── Step 2: Test Metadata ───
st.header("2. Test Metadata")

col1, col2, col3 = st.columns(3)
with col1:
    session_date = st.date_input(
        "Test Date", value=datetime.date.today()
    )
with col2:
    difficulty_level = st.selectbox(
        "Default Difficulty Level",
        options=[1, 2, 3],
        index=1,
        format_func=lambda x: {1: "1 — Easy", 2: "2 — Medium", 3: "3 — Hard"}[x],
    )
with col3:
    sleep_hours = st.number_input(
        "Hours Slept Last Night",
        min_value=0.0, max_value=24.0, value=7.0, step=0.5,
        help="Used for behavioural analysis.",
    )

stress_level = st.slider(
    "Stress Level (1-10)", min_value=1, max_value=10, value=5,
    help="1 = Very Relaxed, 10 = Very Stressed."
)

# ─── Step 3: Auto Topic Tagging via Embeddings ───
st.header("3. Topic Tagging (AI-Assisted)")

syllabus_topics = _get_syllabus_topics()

if not syllabus_topics:
    st.warning(
        "No syllabus topics found in the database. Please go to 'Syllabus Mapping' to "
        "add topics first, or manually enter topic tags below."
    )

# Auto-classify on button click (cached in session state)
state_key = f"topic_tags_{external_test_id}"

if state_key not in st.session_state:
    if syllabus_topics:
        with st.spinner("🔍 Classifying questions using local embedding model..."):
            auto_tags = classify_questions(mcq_data, syllabus_topics)
        st.session_state[state_key] = auto_tags
    else:
        st.session_state[state_key] = ["Uncategorized"] * total_mcq

topic_tags = st.session_state[state_key]

# ─── Step 4: Preview Table with Editable Topic Tags ───
st.header("4. Preview & Adjust")
st.markdown("Review the auto-assigned topic tags. You can **override** any tag below.")

preview_rows = []
for idx, q in enumerate(mcq_data):
    q_text = q.get("question_text", "")
    truncated = (q_text[:80] + "...") if len(q_text) > 80 else q_text
    outcome_icon = "✅" if q.get("outcome", 0) == 1 else "❌"
    preview_rows.append({
        "#": idx + 1,
        "Question": truncated,
        "Options": len(q.get("options", [])),
        "Outcome": outcome_icon,
        "Correct": q.get("correct_answer", "?"),
    })

st.dataframe(pd.DataFrame(preview_rows), use_container_width=True, hide_index=True)

# Per-question topic tag editors
st.subheader("Topic Tag Assignment")
st.caption(
    "Auto-classified using the local embedding model against your syllabus. "
    "Override any tag by selecting from the dropdown or typing a new one."
)

# Build options list: syllabus topics + any auto-assigned that aren't in syllabus
all_tag_options = list(set(syllabus_topics + topic_tags + ["Uncategorized"]))
all_tag_options.sort()

edited_tags = []
cols_per_row = 3
for i in range(0, total_mcq, cols_per_row):
    cols = st.columns(cols_per_row)
    for j, col in enumerate(cols):
        idx = i + j
        if idx >= total_mcq:
            break
        q_text = mcq_data[idx].get("question_text", "")
        short = (q_text[:50] + "...") if len(q_text) > 50 else q_text
        with col:
            default_idx = all_tag_options.index(topic_tags[idx]) if topic_tags[idx] in all_tag_options else 0
            tag = st.selectbox(
                f"Q{idx+1}: {short}",
                options=all_tag_options,
                index=default_idx,
                key=f"tag_{idx}",
            )
            edited_tags.append(tag)

# ─── Step 5: Import Button ───
st.header("5. Import")

col_import, col_diag = st.columns(2)

with col_import:
    do_import = st.button("🚀 Import Test", type="primary", use_container_width=True)

with col_diag:
    run_diag = st.checkbox("Run diagnostics after import", value=True)

if do_import:
    with st.spinner("Importing test data..."):
        try:
            result = import_evalify_test(
                json_data=mcq_data,
                topic_tags=edited_tags,
                difficulty_level=difficulty_level,
                sleep_hours=sleep_hours,
                stress_level=stress_level,
                session_date=session_date.isoformat(),
                student_id=student_id,
            )
            st.success(
                f"✅ **Import Successful!**\n\n"
                f"- **Internal Test ID:** {result['test_id']}\n"
                f"- **External Test ID:** {result['external_test_id']}\n"
                f"- **MCQs Imported:** {result['total_imported']}"
            )
        except Exception as e:
            st.error(f"Import failed: {e}")
            st.stop()

    if run_diag:
        import io, contextlib
        with st.spinner("Running preprocessing and diagnostics..."):
            PreprocessingPipeline().run()

            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                run_diagnostics(student_id)
            diag_output = buffer.getvalue()

        st.success("Diagnostics updated!")
        with st.expander("View Diagnostic Process Log"):
            st.text(diag_output)

    st.balloons()
