import sqlite3
import json
import time
import datetime

def run_test(student_id: int, test_id: int, topic_tag: str) -> list:
    conn = sqlite3.connect("student_helper.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT Question_ID, Question_Text, Options, Correct_Answer, Difficulty_Level
        FROM Questions
        WHERE Student_ID = ? AND Topic_Tag = ? AND Was_Asked = 0
        ORDER BY Question_ID ASC
        LIMIT 5
    ''', (student_id, topic_tag))
    
    questions = cursor.fetchall()
    
    if not questions:
        print(f"No available questions found for topic: {topic_tag}.")
        conn.close()
        return []
        
    answers = []
    
    print(f"\n--- Starting Test on {topic_tag} ---\n")
    
    correct_count = 0
    seq_num = 1
    
    for q in questions:
        q_id, q_text, options_json, correct_ans, difficulty = q
        options = json.loads(options_json)
        
        print(f"Question {seq_num}: {q_text}")
        for opt in options:
            print(opt)
            
        start_time = time.time()
        
        while True:
            student_answer = input("\nYour answer (A/B/C/D): ").strip().upper()
            if student_answer in ["A", "B", "C", "D"]:
                break
            print("Invalid input. Please enter A, B, C, or D.")
            
        end_time = time.time()
        
        time_spent_seconds = end_time - start_time
        time_of_day = datetime.datetime.now().strftime("%H:%M")
        
        outcome = 1 if student_answer == correct_ans else 0
        if outcome == 1:
            correct_count += 1
            
        answers.append({
            'student_id': student_id,
            'test_id': test_id,
            'topic_tag': topic_tag,
            'question_id': q_id,
            'outcome': outcome,
            'time_spent_seconds': time_spent_seconds,
            'difficulty_level': difficulty,
            'test_sequence_number': seq_num,
            'time_of_day': time_of_day
        })
        
        # Mark question as asked
        cursor.execute('''
            UPDATE Questions SET Was_Asked = 1 WHERE Question_ID = ?
        ''', (q_id,))
        
        print("-" * 40)
        seq_num += 1
        
    conn.commit()
    conn.close()
    
    print(f"\nTest Complete! You got {correct_count} out of {len(questions)} correct.")
    return answers
