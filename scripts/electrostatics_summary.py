import sqlite3

def electrostatics_summary(db_path="student_helper.db"):
    """Prints the number of correct and wrong answers for each student in Electrostatics.

    The Academic_Performance_Log table stores each answer with an `Outcome` column
    where 1 = correct and 0 = wrong. This function aggregates those outcomes for the
    topic "Electrostatics" and prints a concise report.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = """
        SELECT
            Student_ID,
            SUM(Outcome) AS correct_answers,
            COUNT(*) - SUM(Outcome) AS wrong_answers
        FROM Academic_Performance_Log
        WHERE Topic_Tag = 'Electrostatics'
        GROUP BY Student_ID
    """
    cursor.execute(query)
    rows = cursor.fetchall()

    if not rows:
        print("No Electrostatics records found.")
    else:
        print("Electrostatics Answer Summary per Student:")
        print(f"{'Student_ID':<12}{'Correct':<10}{'Wrong':<10}")
        for student_id, correct, wrong in rows:
            print(f"{student_id:<12}{correct:<10}{wrong:<10}")

    conn.close()

if __name__ == "__main__":
    electrostatics_summary()
