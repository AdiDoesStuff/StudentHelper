"""
Evalify Test Data Importer
Imports externally-scraped Evalify test data into the AEGIS-MIND database.
Filters out descriptive questions, keeps only MCQs.
"""
import sqlite3
import json
import hashlib
from core.generator.classifier import classify_chunks_batch


def generate_test_id(external_id: str) -> int:
    """
    Deterministic hash of the Evalify string ID to an integer.
    Uses first 8 bytes of SHA-256 to produce a positive 64-bit int.
    """
    hash_bytes = hashlib.sha256(external_id.encode()).digest()[:8]
    return int.from_bytes(hash_bytes, byteorder='big') % (2**31)  # Keep within SQLite INTEGER range


def check_duplicate(external_test_id: str) -> bool:
    """
    Check if a test with this External_Test_ID already exists.
    Returns True if duplicate found.
    """
    conn = sqlite3.connect("student_helper.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM Questions WHERE External_Test_ID = ?",
        (external_test_id,)
    )
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0


def classify_questions(questions: list, syllabus_topics: list) -> list:
    """
    Uses the local embedding model (all-MiniLM-L6-v2) to classify each
    question's text into the best-matching syllabus topic.
    Returns a list of topic tags, one per question.
    """
    if not syllabus_topics:
        return ["Uncategorized"] * len(questions)

    question_texts = [q["question_text"] for q in questions]
    return classify_chunks_batch(question_texts, syllabus_topics, threshold=0.2)


def _get_syllabus_topics() -> list:
    """Fetch all distinct topic names from the Syllabus_Topics table."""
    conn = sqlite3.connect("student_helper.db")
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT Topic_Name FROM Syllabus_Topics ORDER BY Topic_Name")
    topics = [row[0] for row in cursor.fetchall()]
    conn.close()
    return topics


def filter_mcq_only(questions: list) -> list:
    """
    Filters out descriptive / coding questions.
    An MCQ must have a non-empty options list with at least 2 options.
    """
    mcqs = []
    skipped = 0
    for q in questions:
        options = q.get("options", [])
        if isinstance(options, list) and len(options) >= 2:
            mcqs.append(q)
        else:
            skipped += 1
    if skipped > 0:
        print(f"  Filtered out {skipped} non-MCQ (descriptive/coding) question(s).")
    return mcqs


def import_evalify_test(
    json_data: list,
    topic_tags: list,
    difficulty_level: int,
    sleep_hours: float,
    stress_level: int,
    session_date: str,
    student_id: int = 1,
) -> dict:
    """
    Main orchestrator for importing Evalify test data.

    Args:
        json_data: List of question dicts from the Tampermonkey export (MCQ-only, already filtered).
        topic_tags: List of topic tag strings, one per question (from embedding classification or user override).
        difficulty_level: Default difficulty level (1/2/3) for all questions.
        sleep_hours: Hours of sleep for behavioural log.
        stress_level: Stress level (1-10) for behavioural log.
        session_date: ISO date string (e.g. '2026-05-01').
        student_id: Student ID to associate with.

    Returns:
        dict with import summary: {test_id, total_imported, external_test_id, was_duplicate}.
    """
    if not json_data:
        raise ValueError("No questions to import.")

    external_test_id = json_data[0].get("test_id", "unknown")

    # Generate integer test_id from the external string
    test_id = generate_test_id(str(external_test_id))

    conn = sqlite3.connect("student_helper.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Ensure student exists
    cursor.execute(
        "INSERT OR IGNORE INTO Students (Student_ID, Student_Name) VALUES (?, ?)",
        (student_id, "Student")
    )

    # --- Step 1: Insert Behavioural_Log ---
    is_imputed = 0
    if sleep_hours is None:
        is_imputed = 1
        cursor.execute(
            "SELECT AVG(Sleep_Hours) FROM Behavioural_Log WHERE Student_ID = ? AND Sleep_Hours IS NOT NULL AND Is_Imputed = 0",
            (student_id,)
        )
        result = cursor.fetchone()
        sleep_hours = result[0] if (result and result[0] is not None) else 7.0

    cursor.execute('''
        INSERT INTO Behavioural_Log (Student_ID, Test_ID, Sleep_Hours, Stress_Level, Session_Date, Is_Imputed)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (student_id, test_id, sleep_hours, stress_level, session_date, is_imputed))

    # --- Step 2: Insert Questions + Step 3: Insert Academic_Performance_Log ---
    inserted_count = 0
    for idx, q in enumerate(json_data):
        topic_tag = topic_tags[idx] if idx < len(topic_tags) else "Uncategorized"
        options_json = json.dumps(q.get("options", []))

        # Normalize correct answer to single letter if needed
        correct_answer = q.get("correct_answer", "")
        if isinstance(correct_answer, str) and len(correct_answer) == 1:
            correct_answer = correct_answer.upper()

        # Insert into Questions (Was_Asked = 1 since already answered)
        cursor.execute('''
            INSERT INTO Questions
            (Student_ID, Test_ID, Topic_Tag, Question_Text, Options, Correct_Answer,
             Difficulty_Level, Was_Asked, Source, External_Test_ID)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1, 'evalify', ?)
        ''', (
            student_id,
            test_id,
            topic_tag,
            q.get("question_text", ""),
            options_json,
            correct_answer,
            difficulty_level,
            str(external_test_id),
        ))

        db_question_id = cursor.lastrowid

        # Ensure Student_Profile row exists for this topic
        cursor.execute(
            "INSERT OR IGNORE INTO Student_Profile (Student_ID, Topic_Tag, Concept_Weightage) VALUES (?, ?, 1.0)",
            (student_id, topic_tag)
        )

        # Insert into Academic_Performance_Log
        outcome = q.get("outcome", 0)
        seq_num = q.get("test_sequence_number", idx + 1)

        cursor.execute('''
            INSERT INTO Academic_Performance_Log
            (Student_ID, Test_ID, Topic_Tag, Question_ID, Outcome,
             Time_Spent_Seconds, Difficulty_Level, Time_of_Day, Test_Sequence_Number, Is_Lucky_Guess)
            VALUES (?, ?, ?, ?, ?, NULL, ?, NULL, ?, NULL)
        ''', (
            student_id,
            test_id,
            topic_tag,
            db_question_id,
            outcome,
            difficulty_level,
            seq_num,
        ))

        inserted_count += 1

    conn.commit()
    conn.close()

    return {
        "test_id": test_id,
        "external_test_id": external_test_id,
        "total_imported": inserted_count,
    }
