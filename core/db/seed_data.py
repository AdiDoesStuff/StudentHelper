import sqlite3
import random
import os
import sys

# Ensure root directory is in sys.path so 'core...' imports work when running directly
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grandparent_dir = os.path.dirname(parent_dir)
if grandparent_dir not in sys.path:
    sys.path.insert(0, grandparent_dir)

from core.db.database_init import init_db

def seed_data():
    init_db()

    conn = sqlite3.connect("student_helper.db")
    cursor = conn.cursor()

    # Enable foreign keys to enforce strict schema adherence
    cursor.execute("PRAGMA foreign_keys = ON;")

    print("Clearing out old data...")
    # Clear existing data so we always get a fresh predictable seed
    cursor.execute("DELETE FROM Academic_Performance_Log")
    cursor.execute("DELETE FROM Behavioural_Log")
    cursor.execute("DELETE FROM Student_Profile")
    cursor.execute("DELETE FROM Students")

    print("Seeding data")

    # Insert two students
    cursor.execute("INSERT INTO Students (Student_ID, Student_Name) VALUES (?, ?)", (1, "Aditya"))
    cursor.execute("INSERT INTO Students (Student_ID, Student_Name) VALUES (?, ?)", (2, "Mathy"))

    # Define a richer set of topics
    topics = ["Quantum Gates", "Thermodynamics", "Kinematics", "Electrostatics", "Linear Algebra", "Data Structures"]

    # Create Student_Profile entries for each student with varied concept weightages
    for student_id in (1, 2):
        for topic in topics:
            cursor.execute('''INSERT INTO Student_Profile 
                              (Student_ID, Topic_Tag, Concept_Weightage) 
                              VALUES (?, ?, ?)''', (student_id, topic, round(random.uniform(0.4, 1.2), 2)))

    # Insert Behavioural Logs (Simulated Tests) for both students
    test_ids_student1 = [101, 102, 103, 104]
    test_ids_student2 = [201, 202, 203, 204]

    # Student 1: Intentional missing Sleep_Hours for first test
    cursor.execute('''INSERT INTO Behavioural_Log 
                      (Student_ID, Test_ID, Sleep_Hours, Stress_Level, Session_Duration_Seconds) 
                      VALUES (?, ?, NULL, ?, ?)''', (1, 101, 7, 600.0))
    # Student 2: Intentional missing Sleep_Hours for first test as well
    cursor.execute('''INSERT INTO Behavioural_Log 
                      (Student_ID, Test_ID, Sleep_Hours, Stress_Level, Session_Duration_Seconds) 
                      VALUES (?, ?, NULL, ?, ?)''', (2, 201, 6, 550.0))

    # Remaining tests for both students - normal randomized logs
    for sid, test_ids in ((1, test_ids_student1[1:]), (2, test_ids_student2[1:])):
        for test_id in test_ids:
            cursor.execute('''INSERT INTO Behavioural_Log 
                              (Student_ID, Test_ID, Sleep_Hours, Stress_Level, Session_Duration_Seconds) 
                              VALUES (?, ?, ?, ?, ?)''', 
                           (sid, test_id, round(random.uniform(5.5, 9.0), 1), random.randint(1, 10), round(random.uniform(1200.0, 3600.0), 1)))

    # Insert Academic Logs with outliers for the first test of each student
    # Test 101 (Student 1) - deterministic messy data for IQR / Min-Max pipeline testing
    messy_test_data_student1 = [
        (1, 101, 'Quantum Gates', 1, 1, 45.0, 2, 1),
        (1, 101, 'Quantum Gates', 2, 1, 42.0, 2, 2),
        (1, 101, 'Quantum Gates', 3, 1, 38.0, 2, 3),
        (1, 101, 'Quantum Gates', 4, 1, 41.0, 2, 4),
        (1, 101, 'Quantum Gates', 5, 1, 0.5,  3, 5),  # OUTLIER - likely random guess
        (1, 101, 'Quantum Gates', 6, 1, 1.2,  3, 6),  # OUTLIER - likely random guess
        (1, 101, 'Thermodynamics', 7, 0, 350.5, 3, 7) # OUTLIER - extremely slow and incorrect
    ]
    # Test 201 (Student 2) - similar pattern with different values
    messy_test_data_student2 = [
        (2, 201, 'Linear Algebra', 1, 1, 48.0, 2, 1),
        (2, 201, 'Linear Algebra', 2, 1, 44.0, 2, 2),
        (2, 201, 'Linear Algebra', 3, 1, 39.0, 2, 3),
        (2, 201, 'Linear Algebra', 4, 1, 43.0, 2, 4),
        (2, 201, 'Linear Algebra', 5, 1, 0.7,  3, 5),  # OUTLIER
        (2, 201, 'Linear Algebra', 6, 1, 1.0,  3, 6),  # OUTLIER
        (2, 201, 'Data Structures', 7, 0, 340.0, 3, 7) # OUTLIER
    ]
    cursor.executemany('''INSERT INTO Academic_Performance_Log 
                          (Student_ID, Test_ID, Topic_Tag, Question_ID, Outcome, Time_Spent_Seconds, Difficulty_Level, Test_Sequence_Number)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', messy_test_data_student1)
    cursor.executemany('''INSERT INTO Academic_Performance_Log 
                          (Student_ID, Test_ID, Topic_Tag, Question_ID, Outcome, Time_Spent_Seconds, Difficulty_Level, Test_Sequence_Number)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', messy_test_data_student2)

    # Random distributed data for the remaining tests of both students
    q_id_counter = 8
    for sid, test_ids in ((1, test_ids_student1[1:]), (2, test_ids_student2[1:])):
        for test_id in test_ids:
            for seq in range(1, 16):  # 15 questions per test
                topic = random.choice(topics)
                outcome = random.choice([0, 1])
                time_spent = round(random.uniform(20.0, 120.0), 1)
                difficulty = random.choice([1, 2, 3])
                cursor.execute("""
                    INSERT INTO Academic_Performance_Log 
                    (Student_ID, Test_ID, Topic_Tag, Question_ID, Outcome,
                     Time_Spent_Seconds, Difficulty_Level, Test_Sequence_Number)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                               (sid, test_id, topic, q_id_counter, outcome, time_spent, difficulty, seq))
                q_id_counter += 1

    conn.commit()
    conn.close()
    print("seeded successfully")

if __name__ == "__main__":
    seed_data()
