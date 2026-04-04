import sqlite3

def init_db():
    conn = sqlite3.connect("student_helper.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. STUDENTS TABLE
    cursor.execute('''CREATE TABLE IF NOT EXISTS Students (
        Student_ID INTEGER PRIMARY KEY,
        Student_Name TEXT NOT NULL
    );''')

    # 2. STUDENT PROFILE
    cursor.execute('''CREATE TABLE IF NOT EXISTS Student_Profile (
        Student_ID INTEGER NOT NULL,
        Topic_Tag TEXT NOT NULL,
        Weakness_Index REAL DEFAULT 0.0,
        Concept_Weightage REAL DEFAULT 1.0,
        Last_Tested_Date TEXT,
        Session_Cluster_State TEXT,
        Total_Sessions INTEGER DEFAULT 0,
        Average_Accuracy REAL DEFAULT 0.0,
        Cumulative_Time_Spent REAL DEFAULT 0.0,
        PRIMARY KEY (Student_ID, Topic_Tag),
        FOREIGN KEY (Student_ID) REFERENCES Students (Student_ID)
    );''')

    # 3. BEHAVIOURAL LOG
    cursor.execute('''CREATE TABLE IF NOT EXISTS Behavioural_Log (
        Session_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Student_ID INTEGER NOT NULL,
        Test_ID INTEGER UNIQUE NOT NULL, 
        Sleep_Hours REAL,
        Stress_Level INTEGER CHECK (Stress_Level BETWEEN 1 AND 10),
        Session_Date TEXT DEFAULT CURRENT_DATE,
        Session_Duration_Seconds REAL,
        Is_Imputed INTEGER DEFAULT 0 CHECK (Is_Imputed IN (0, 1)),
        FOREIGN KEY (Student_ID) REFERENCES Students (Student_ID)
    );''')

    # 4. ACADEMIC LOG
    cursor.execute('''CREATE TABLE IF NOT EXISTS Academic_Performance_Log (
        Log_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Student_ID INTEGER NOT NULL,
        Test_ID INTEGER NOT NULL,
        Topic_Tag TEXT NOT NULL,
        Question_ID INTEGER NOT NULL,
        Outcome INTEGER NOT NULL CHECK (Outcome IN (0,1)),
        Time_Spent_Seconds REAL,
        Difficulty_Level INTEGER NOT NULL CHECK (Difficulty_Level IN (1,2,3)),
        Time_of_Day TEXT,
        Test_Sequence_Number INTEGER NOT NULL,
        Is_Lucky_Guess INTEGER DEFAULT NULL,
        FOREIGN KEY (Test_ID) REFERENCES Behavioural_Log (Test_ID),
        FOREIGN KEY (Student_ID, Topic_Tag) REFERENCES Student_Profile (Student_ID, Topic_Tag)
    );''')

    conn.commit()
    conn.close()
    print('database ready')

if __name__ == "__main__":
    init_db()