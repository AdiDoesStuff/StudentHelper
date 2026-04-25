import sqlite3
import json

def inspect_latest_test():
    conn = sqlite3.connect("student_helper.db")
    cursor = conn.cursor()
    
    # Get latest behavioral log
    cursor.execute("SELECT * FROM Behavioural_Log ORDER BY Session_ID DESC LIMIT 1")
    behavioral = cursor.fetchone()
    if not behavioral:
        print("No behavioral log found.")
        return
    
    session_id, student_id, test_id, sleep, stress, date, duration, is_imputed = behavioral
    print(f"Latest Test ID: {test_id}")
    print(f"Student ID: {student_id}")
    print(f"Sleep: {sleep}, Stress: {stress}, Date: {date}")
    
    # Get questions for this test
    cursor.execute("SELECT Topic_Tag, COUNT(*) FROM Academic_Performance_Log WHERE Test_ID = ? GROUP BY Topic_Tag", (test_id,))
    topics = cursor.fetchall()
    print("Topics and Question counts:")
    for topic, count in topics:
        print(f" - {topic}: {count}")
        
    # Get all questions details to replicate them (or at least the count/topic distribution)
    cursor.execute("SELECT Question_ID, Topic_Tag, Difficulty_Level, Outcome FROM Academic_Performance_Log WHERE Test_ID = ?", (test_id,))
    questions = cursor.fetchall()
    print(f"Total Questions: {len(questions)}")
    
    conn.close()

if __name__ == "__main__":
    inspect_latest_test()
