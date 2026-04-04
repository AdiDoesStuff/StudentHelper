import sqlite3
import random
from database_init import init_db

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

    cursor.execute("INSERT INTO Students (Student_ID, Student_Name) VALUES (?, ?)", (1, "Aditya"))
    
    topics = ["Quantum Gates", "Thermodynamics", "Kinematics", "Electrostatics"]
    
    # 3. Create Topics in Student_Profile
    for topic in topics:
        # Give random concept weights to mimic different baseline difficulty
        cursor.execute('''INSERT INTO Student_Profile 
                          (Student_ID, Topic_Tag, Concept_Weightage) 
                          VALUES (?, ?, ?)''', (1, topic, round(random.uniform(0.5, 1.0), 2)))

    # 4. Insert Behavioural Logs (Simulated Tests)
    test_ids = [101, 102, 103, 104]
    
    # Test 101: INTENTIONALLY Missing Data (NULL Sleep_Hours) for Phase 1 Imputation testing
    cursor.execute('''INSERT INTO Behavioural_Log 
                      (Student_ID, Test_ID, Sleep_Hours, Stress_Level, Session_Duration_Seconds) 
                      VALUES (?, ?, NULL, ?, ?)''', (1, 101, 7, 600.0))

    # Test 102 - 104: Normal randomized behavioral logs
    for test_id in test_ids[1:]:
        cursor.execute('''INSERT INTO Behavioural_Log 
                          (Student_ID, Test_ID, Sleep_Hours, Stress_Level, Session_Duration_Seconds) 
                          VALUES (?, ?, ?, ?, ?)''', 
                       (1, test_id, round(random.uniform(5.5, 9.0), 1), random.randint(1, 10), round(random.uniform(1200.0, 3600.0), 1)))

    # 5. Insert Academic Logs with Outliers (Fast/Slow guesses)
    # Format: (Student_ID, Test_ID, Topic, Q_ID, Outcome, Time, Difficulty, Seq)
    
    # Deterministic messy data for Test 101 -> Ideal for testing your IQR / Min-Max pipeline
    messy_test_data = [
        (1, 101, 'Quantum Gates', 1, 1, 45.0, 2, 1), # Normal
        (1, 101, 'Quantum Gates', 2, 1, 42.0, 2, 2), # Normal
        (1, 101, 'Quantum Gates', 3, 1, 38.0, 2, 3), # Normal
        (1, 101, 'Quantum Gates', 4, 1, 41.0, 2, 4), # Normal
        (1, 101, 'Quantum Gates', 5, 1, 0.5,  3, 5), # OUTLIER (Hard question answered in 0.5s -> likely random guess)
        (1, 101, 'Quantum Gates', 6, 1, 1.2,  3, 6), # OUTLIER (Hard question answered in 1.2s -> likely random guess)
        (1, 101, 'Thermodynamics', 7, 0, 350.5, 3, 7) # OUTLIER (Extremely slow and Incorrect)
    ]
    cursor.executemany('''INSERT INTO Academic_Performance_Log 
                          (Student_ID, Test_ID, Topic_Tag, Question_ID, Outcome, Time_Spent_Seconds, Difficulty_Level, Test_Sequence_Number)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', messy_test_data)

    # Random distributed data for the other tests (102, 103, 104)
    q_id_counter = 8
    for test_id in test_ids[1:]:
        for seq in range(1, 16): # 15 questions per test
            topic = random.choice(topics)
            outcome = random.choice([0, 1])
            # Simulated normal distribution of time spent (20s to 120s typically)
            time_spent = round(random.uniform(20.0, 120.0), 1)
            difficulty = random.choice([1, 2, 3])

            cursor.execute("""
                INSERT INTO Academic_Performance_Log 
                (Student_ID, Test_ID, Topic_Tag, Question_ID, Outcome,
                 Time_Spent_Seconds, Difficulty_Level, Test_Sequence_Number)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (1, test_id, topic, q_id_counter, outcome, time_spent, difficulty, seq))
            q_id_counter += 1

    conn.commit()
    conn.close()
    print("seeded successfully")

if __name__ == "__main__":
    seed_data()
