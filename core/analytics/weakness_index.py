import sqlite3
import pandas as pd

def compute_weakness():
    """
    Module 1: Weakness Index Calculation.
    Logic: W = (1 - Accuracy) * Concept_Weightage

    Also ensures that Student_Profile rows exist for every
    (Student_ID, Topic_Tag) seen in the Academic_Performance_Log,
    so that the subsequent UPDATE always hits a real row.
    """
    conn = sqlite3.connect("student_helper.db")
    cursor = conn.cursor()

    # 0. Ensure the default student (ID=1) exists so FK constraints don't fire
    cursor.execute("""
        INSERT OR IGNORE INTO Students (Student_ID, Student_Name)
        VALUES (1, 'Student')
    """)
    conn.commit()

    # 1. Load data and filter out lucky guesses
    query = """
    SELECT Student_ID, Topic_Tag, AVG(Outcome) as Accuracy
    FROM Academic_Performance_Log
    WHERE Is_Lucky_Guess != 1 OR Is_Lucky_Guess IS NULL
    GROUP BY Student_ID, Topic_Tag
    """
    accuracy_df = pd.read_sql_query(query, conn)

    if accuracy_df.empty:
        print("Module 1: No performance data found. Skipping.")
        conn.close()
        return

    # 2. Seed Student_Profile rows for every unseen (Student_ID, Topic_Tag).
    #    INSERT OR IGNORE leaves any existing rows untouched.
    for _, row in accuracy_df.iterrows():
        cursor.execute("""
            INSERT OR IGNORE INTO Student_Profile (Student_ID, Topic_Tag, Concept_Weightage)
            VALUES (?, ?, 1.0)
        """, (int(row['Student_ID']), row['Topic_Tag']))
    conn.commit()

    # 3. Join with Student_Profile to get Concept_Weightage
    profile_df = pd.read_sql_query(
        "SELECT Student_ID, Topic_Tag, Concept_Weightage FROM Student_Profile", conn
    )
    merged = pd.merge(accuracy_df, profile_df, on=["Student_ID", "Topic_Tag"])

    # 4. Calculate Weakness Index
    merged['Weakness_Index'] = (1 - merged['Accuracy']) * merged['Concept_Weightage']

    # 5. Update Student_Profile with the computed metrics
    for _, row in merged.iterrows():
        cursor.execute("""
            UPDATE Student_Profile
            SET Weakness_Index = ?, Average_Accuracy = ?
            WHERE Student_ID = ? AND Topic_Tag = ?
        """, (
            float(row['Weakness_Index']),
            float(row['Accuracy']),
            int(row['Student_ID']),
            row['Topic_Tag']
        ))

    conn.commit()
    conn.close()
    print(f"Module 1: Weakness Index Updated for {len(merged)} topic(s).")


if __name__ == "__main__":
    compute_weakness()
