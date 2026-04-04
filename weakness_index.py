import sqlite3
import pandas as pd

def compute_weakness():
    """
    Module 1: Weakness Index Calculation.
    Logic: W = (1 - Accuracy) * Concept_Weightage
    """
    conn = sqlite3.connect("student_helper.db")
    
    # 1. Load data and filter out lucky guesses
    # We pull from Academic_Performance_Log but exclude Is_Lucky_Guess = 1
    query = """
    SELECT Student_ID, Topic_Tag, AVG(Outcome) as Accuracy
    FROM Academic_Performance_Log
    WHERE Is_Lucky_Guess != 1 OR Is_Lucky_Guess IS NULL
    GROUP BY Student_ID, Topic_Tag
    """
    accuracy_df = pd.read_sql_query(query, conn)

    # 2. Join with Student_Profile to get Concept_Weightage
    profile_df = pd.read_sql_query("SELECT Student_ID, Topic_Tag, Concept_Weightage FROM Student_Profile", conn)
    merged = pd.merge(accuracy_df, profile_df, on=["Student_ID", "Topic_Tag"])

    # 3. Calculate Weakness Index
    merged['Weakness_Index'] = (1 - merged['Accuracy']) * merged['Concept_Weightage']

    # 4. Update Student_Profile with computed metrics
    cursor = conn.cursor()
    for _, row in merged.iterrows():
        cursor.execute("""
            UPDATE Student_Profile 
            SET Weakness_Index = ?, Average_Accuracy = ?
            WHERE Student_ID = ? AND Topic_Tag = ?
        """, (float(row['Weakness_Index']), float(row['Accuracy']), int(row['Student_ID']), row['Topic_Tag']))
    
    conn.commit()
    conn.close()
    print("✅ Module 1: Weakness Index Updated.")

if __name__ == "__main__":
    compute_weakness()
