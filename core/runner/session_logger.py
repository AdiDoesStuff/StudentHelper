import sqlite3
import datetime

def create_session(student_id: int, test_id: int, sleep_hours: float, stress_level: int) -> int:
    conn = sqlite3.connect("student_helper.db")
    cursor = conn.cursor()
    
    session_date = datetime.date.today().isoformat()
    is_imputed = 0
    
    if sleep_hours is None:
        is_imputed = 1
        # Retrieve historical mean sleep
        cursor.execute('''
            SELECT AVG(Sleep_Hours) FROM Behavioural_Log 
            WHERE Student_ID = ? AND Sleep_Hours IS NOT NULL AND Is_Imputed = 0
        ''', (student_id,))
        result = cursor.fetchone()
        
        if result and result[0] is not None:
            sleep_hours = result[0]
        else:
            sleep_hours = 7.0
            
    cursor.execute('''
        INSERT INTO Behavioural_Log (Student_ID, Test_ID, Sleep_Hours, Stress_Level, Session_Date, Is_Imputed)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (student_id, test_id, sleep_hours, stress_level, session_date, is_imputed))
    
    conn.commit()
    conn.close()
    
    return test_id

def log_answers(answers: list) -> None:
    if not answers:
        return
        
    conn = sqlite3.connect("student_helper.db")
    cursor = conn.cursor()
    
    total_time_spent = 0.0
    student_id = answers[0]['student_id']
    test_id = answers[0]['test_id']
    topic_tag = answers[0]['topic_tag']
    
    for ans in answers:
        cursor.execute('''
            INSERT INTO Academic_Performance_Log 
            (Student_ID, Test_ID, Topic_Tag, Question_ID, Outcome, Time_Spent_Seconds, Difficulty_Level, Time_of_Day, Test_Sequence_Number, Is_Lucky_Guess)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)
        ''', (
            ans['student_id'],
            ans['test_id'],
            ans['topic_tag'],
            ans['question_id'],
            ans['outcome'],
            ans['time_spent_seconds'],
            ans['difficulty_level'],
            ans['time_of_day'],
            ans['test_sequence_number']
        ))
        total_time_spent += ans['time_spent_seconds']
        
    cursor.execute('''
        UPDATE Behavioural_Log 
        SET Session_Duration_Seconds = ?
        WHERE Test_ID = ?
    ''', (total_time_spent, test_id))
    
    # Also update Student_Profile
    today_date = datetime.date.today().isoformat()
    cursor.execute('''
        UPDATE Student_Profile 
        SET Total_Sessions = Total_Sessions + 1,
            Last_Tested_Date = ?
        WHERE Student_ID = ? AND Topic_Tag = ?
    ''', (today_date, student_id, topic_tag))
    
    conn.commit()
    conn.close()
