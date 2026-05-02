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

    # 4. QUESTIONS TABLE
    cursor.execute('''CREATE TABLE IF NOT EXISTS Questions (
        Question_ID      INTEGER PRIMARY KEY AUTOINCREMENT,
        Student_ID       INTEGER NOT NULL,
        Test_ID          INTEGER NOT NULL,
        Topic_Tag        TEXT NOT NULL,
        Question_Text    TEXT NOT NULL,
        Options          TEXT NOT NULL,
        Correct_Answer   TEXT NOT NULL,
        Difficulty_Level INTEGER NOT NULL CHECK (Difficulty_Level IN (1, 2, 3)),
        Was_Asked        INTEGER DEFAULT 0 CHECK (Was_Asked IN (0, 1)),
        Source           TEXT DEFAULT 'internal',
        External_Test_ID TEXT,
        FOREIGN KEY (Student_ID) REFERENCES Students (Student_ID),
        FOREIGN KEY (Test_ID)    REFERENCES Behavioural_Log (Test_ID)
    );''')

    cursor.execute('''CREATE INDEX IF NOT EXISTS idx_questions_topic 
    ON Questions (Student_ID, Topic_Tag, Was_Asked);''')

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

    # 6. SYLLABUS TOPICS TABLE
    cursor.execute('''CREATE TABLE IF NOT EXISTS Syllabus_Topics (
        Subject_Name TEXT NOT NULL,
        Unit_Number  INTEGER NOT NULL,
        Topic_Name   TEXT NOT NULL,
        Topic_Order  INTEGER NOT NULL,
        PRIMARY KEY (Subject_Name, Unit_Number, Topic_Order)
    );''')

    # 7. STUDY AVAILABILITY
    cursor.execute('''CREATE TABLE IF NOT EXISTS Study_Availability (
        Availability_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Student_ID INTEGER NOT NULL,
        Day_of_Week TEXT NOT NULL, 
        Start_Time TEXT, 
        End_Time TEXT,
        FOREIGN KEY (Student_ID) REFERENCES Students (Student_ID)
    );''')

    # 8. WEEKLY TEST SCHEDULE
    cursor.execute('''CREATE TABLE IF NOT EXISTS Weekly_Test_Schedule (
        Schedule_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Student_ID INTEGER NOT NULL,
        Subject_Name TEXT NOT NULL,
        Day_of_Week TEXT NOT NULL,
        FOREIGN KEY (Student_ID) REFERENCES Students (Student_ID)
    );''')

    # 9. TEST INSTANCES
    cursor.execute('''CREATE TABLE IF NOT EXISTS Test_Instances (
        Instance_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Student_ID INTEGER NOT NULL,
        Subject_Name TEXT NOT NULL,
        Test_Date TEXT NOT NULL, 
        Is_Imported INTEGER DEFAULT 0 CHECK (Is_Imported IN (0, 1)),
        FOREIGN KEY (Student_ID) REFERENCES Students (Student_ID)
    );''')

    # 10. STUDY PLAN STATE
    cursor.execute('''CREATE TABLE IF NOT EXISTS Study_Plan_State (
        Plan_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Student_ID INTEGER NOT NULL,
        Generated_Date TEXT NOT NULL, 
        Plan_JSON TEXT NOT NULL, 
        Valid_Until TEXT, 
        FOREIGN KEY (Student_ID) REFERENCES Students (Student_ID)
    );''')

    conn.commit()
    conn.close()
    print('database ready')

def migrate_db():
    """Safely add new columns to existing tables without data loss."""
    conn = sqlite3.connect("student_helper.db")
    cursor = conn.cursor()

    migrations = [
        ("Questions", "Source", "TEXT DEFAULT 'internal'"),
        ("Questions", "External_Test_ID", "TEXT"),
    ]

    for table, column, col_def in migrations:
        try:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_def}")
            print(f"  Added column {table}.{column}")
        except sqlite3.OperationalError:
            # Column already exists — safe to ignore
            pass

    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    init_db()
    migrate_db()