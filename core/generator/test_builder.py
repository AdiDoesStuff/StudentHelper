import sqlite3
import math
import random
from core.generator.rag_engine import retrieve_chunks
from core.generator.question_generator import generate_questions
from core.runner.session_logger import create_session

def build_test(student_id: int, subject: str, topics: list, num_questions: int, sleep_hours: float, stress_level: int, ai_provider: str = "Gemini") -> int:
    """
    Distributes num_questions across the provided topics.
    For each topic, retrieves chunks via RAG, generates questions via LLM.
    Creates a session in Behavioural_Log, inserts questions into Questions table.
    Returns the new test_id.
    """
    
    if not topics:
        raise ValueError("At least one topic must be selected.")
    if num_questions <= 0:
        raise ValueError("Number of questions must be greater than 0.")
        
    num_topics = len(topics)
    base_questions_per_topic = num_questions // num_topics
    remainder = num_questions % num_topics
    
    questions_per_topic = {}
    for i, topic in enumerate(topics):
        count = base_questions_per_topic + (1 if i < remainder else 0)
        questions_per_topic[topic] = count
        
    all_generated_questions = []
    
    for topic, count in questions_per_topic.items():
        if count == 0:
            continue
            
        chunks = retrieve_chunks(topic, k=min(max(count * 3, 6), 15)) # Ensure at least 6 chunks, up to 15
        
        # In case we can't get any chunks, skip
        if not chunks:
            continue
            
        # Call generate questions
        try:
            generated = generate_questions(chunks, num_questions=count, ai_provider=ai_provider)
            # Add topic info to each question so we can store it properly
            for q in generated:
                q['topic_tag'] = topic
            all_generated_questions.extend(generated)
        except Exception as e:
            print(f"Failed to generate questions for topic '{topic}': {e}")
            
    # Shuffle the generated questions so topics are mixed
    random.shuffle(all_generated_questions)
    
    # Trim to exactly num_questions just in case
    all_generated_questions = all_generated_questions[:num_questions]
    
    if not all_generated_questions:
        raise RuntimeError("Failed to generate any questions. Please check context or API.")

    # 1. Get new Test ID
    conn = sqlite3.connect("student_helper.db")
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(Test_ID) FROM Behavioural_Log")
    max_id = cursor.fetchone()[0]
    test_id = (max_id or 0) + 1
    conn.close()
    
    # 2. Create Session
    create_session(student_id, test_id, sleep_hours, stress_level)
    
    # 3. Insert Questions
    conn = sqlite3.connect("student_helper.db")
    cursor = conn.cursor()
    for q in all_generated_questions:
        options_str = str(q['options']).replace("'", '"') # basic json serialization
        import json
        options_str = json.dumps(q['options'])
        
        cursor.execute('''
            INSERT INTO Questions (Student_ID, Test_ID, Topic_Tag, Question_Text, Options, Correct_Answer, Difficulty_Level, Was_Asked)
            VALUES (?, ?, ?, ?, ?, ?, ?, 0)
        ''', (
            student_id,
            test_id,
            q['topic_tag'],
            q['question'],
            options_str,
            q['correct_answer'],
            q['difficulty']
        ))
        
    conn.commit()
    conn.close()
    
    return test_id

def build_revision_test(student_id: int, subject: str, topics: list, num_questions: int, sleep_hours: float, stress_level: int) -> int:
    """
    Creates a new test session using only questions the student has previously gotten wrong
    (Outcome = 0) in the given subject and topics.
    """
    if not topics:
        raise ValueError("At least one topic must be selected.")
    if num_questions <= 0:
        raise ValueError("Number of questions must be greater than 0.")
        
    conn = sqlite3.connect("student_helper.db")
    
    placeholders = ",".join(["?"] * len(topics))
    query = f"""
        SELECT q.Topic_Tag, q.Question_Text, q.Options, q.Correct_Answer, q.Difficulty_Level
        FROM Questions q
        JOIN Academic_Performance_Log a ON q.Question_ID = a.Question_ID
        JOIN Syllabus_Topics s ON q.Topic_Tag = s.Topic_Name
        WHERE a.Student_ID = ? AND a.Outcome = 0 AND s.Subject_Name = ?
        AND q.Topic_Tag IN ({placeholders})
        GROUP BY q.Question_Text
    """
    
    params = [student_id, subject] + topics
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        raise RuntimeError(f"No previous mistakes found for the selected topics in {subject}.")
        
    wrong_questions = []
    for r in rows:
        wrong_questions.append({
            'topic_tag': r[0],
            'question': r[1],
            'options': r[2], # already a json string
            'correct_answer': r[3],
            'difficulty': r[4]
        })
        
    random.shuffle(wrong_questions)
    wrong_questions = wrong_questions[:num_questions]
    
    conn = sqlite3.connect("student_helper.db")
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(Test_ID) FROM Behavioural_Log")
    max_id = cursor.fetchone()[0]
    test_id = (max_id or 0) + 1
    conn.close()
    
    create_session(student_id, test_id, sleep_hours, stress_level)
    
    conn = sqlite3.connect("student_helper.db")
    cursor = conn.cursor()
    for q in wrong_questions:
        cursor.execute('''
            INSERT INTO Questions (Student_ID, Test_ID, Topic_Tag, Question_Text, Options, Correct_Answer, Difficulty_Level, Was_Asked, Source)
            VALUES (?, ?, ?, ?, ?, ?, ?, 0, 'revision')
        ''', (
            student_id,
            test_id,
            q['topic_tag'],
            q['question'],
            q['options'],
            q['correct_answer'],
            q['difficulty']
        ))
        
    conn.commit()
    conn.close()
    
    return test_id
