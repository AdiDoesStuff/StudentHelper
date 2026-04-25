import sqlite3
import random
from datetime import datetime, timedelta
import sys
import os

# Add core to path to use compute_weakness if needed
sys.path.append(os.getcwd())
from core.analytics.weakness_index import compute_weakness

def generate_fake_data():
    conn = sqlite3.connect("student_helper.db")
    cursor = conn.cursor()
    
    # 1. Get original data from Test ID 2 (which the user just did)
    cursor.execute("SELECT Student_ID, Sleep_Hours, Stress_Level, Session_Duration_Seconds FROM Behavioural_Log WHERE Test_ID = 2")
    orig_beh = cursor.fetchone()
    if not orig_beh:
        print("Test ID 2 not found. Using defaults.")
        student_id, stress, duration = 1, 8, 300
    else:
        student_id, _, stress, duration = orig_beh
    
    cursor.execute("SELECT Topic_Tag, Question_Text, Options, Correct_Answer, Difficulty_Level FROM Questions WHERE Test_ID = 2")
    orig_questions = cursor.fetchall()
    
    if not orig_questions:
        print("No questions found for Test ID 2. Aborting.")
        return

    cursor.execute("SELECT MAX(Test_ID) FROM Behavioural_Log")
    max_test_id = cursor.fetchone()[0] or 2
    
    base_date = datetime.strptime("2026-04-25", "%Y-%m-%d")
    
    # Target topic for bad performance
    bad_topic = "HTML 5 Elements"
    
    print(f"Generating 4 tests starting from Test ID {max_test_id + 1}...")
    
    for i in range(1, 5):
        new_test_id = max_test_id + i
        
        # Conditions based on requirements:
        # - 4 more tests
        # - Continuous bad performance in one topic (HTML 5 Elements)
        # - Sleep extremely low for 3 tests, really good for 1
        # - 100% score in the good sleep test
        
        if i < 4:
            # Tests 1-3: Low sleep, bad performance in bad_topic
            sleep = round(random.uniform(2.0, 3.5), 1)
            is_100 = False
            print(f"Test {new_test_id}: Low Sleep ({sleep}h), Bad performance in {bad_topic}")
        else:
            # Test 4: Good sleep, 100% performance
            sleep = 8.5
            is_100 = True
            print(f"Test {new_test_id}: Good Sleep ({sleep}h), 100% Score!")
            
        test_date = (base_date + timedelta(days=i)).strftime("%Y-%m-%d")
        
        # 2. Insert Behavioural_Log
        cursor.execute("""
            INSERT INTO Behavioural_Log (Student_ID, Test_ID, Sleep_Hours, Stress_Level, Session_Date, Session_Duration_Seconds)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (student_id, new_test_id, sleep, stress, test_date, duration))
        
        # 3. Insert Questions and Academic_Performance_Log
        for q_idx, (topic, text, options, answer, diff) in enumerate(orig_questions):
            # Insert Question (copy from test 2)
            cursor.execute("""
                INSERT INTO Questions (Student_ID, Test_ID, Topic_Tag, Question_Text, Options, Correct_Answer, Difficulty_Level, Was_Asked)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1)
            """, (student_id, new_test_id, topic, text, options, answer, diff))
            new_q_id = cursor.lastrowid
            
            # Determine Outcome
            if is_100:
                outcome = 1
            else:
                if topic == bad_topic:
                    # Continuous bad performance: 0/1 outcome
                    outcome = 0 if random.random() < 0.8 else 1 
                else:
                    # Varied performance in other topics: mostly okay
                    outcome = 1 if random.random() < 0.7 else 0
            
            time_spent = round(random.uniform(10, 50), 2)
            time_of_day = "14:00"
            
            cursor.execute("""
                INSERT INTO Academic_Performance_Log (
                    Student_ID, Test_ID, Topic_Tag, Question_ID, Outcome, 
                    Time_Spent_Seconds, Difficulty_Level, Time_of_Day, Test_Sequence_Number, Is_Lucky_Guess
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
            """, (student_id, new_test_id, topic, new_q_id, outcome, time_spent, diff, time_of_day, q_idx + 1))

    conn.commit()
    conn.close()
    
    # 4. Update analytics
    print("Updating analytics...")
    compute_weakness()
    print("Done!")

if __name__ == "__main__":
    generate_fake_data()
