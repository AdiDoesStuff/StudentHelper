import sqlite3
import json

def store_questions(questions: list, student_id: int, test_id: int, topic_tag: str) -> int:
    conn = sqlite3.connect("student_helper.db")
    cursor = conn.cursor()
    
    inserted_count = 0
    for q in questions:
        try:
            # Serialize the options list to JSON
            options_json = json.dumps(q['options'])
            
            cursor.execute('''
                INSERT INTO Questions (Student_ID, Test_ID, Topic_Tag, Question_Text, Options, Correct_Answer, Difficulty_Level)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                student_id,
                test_id,
                topic_tag,
                q['question'],
                options_json,
                q['correct_answer'],
                q['difficulty']
            ))
            inserted_count += 1
        except Exception as e:
            print(f"Failed to insert question: {q.get('question', 'Unknown')}. Error: {e}")
            
    conn.commit()
    conn.close()
    
    return inserted_count
