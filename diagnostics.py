import sqlite3
import pandas as pd
from weakness_index import compute_weakness
from kurtosis_analysis import analyze_kurtosis
from environmental_correlation import analyze_environmental_correlation
from knowledge_graph import build_knowledge_graph, get_root_causes


def get_student_correlation(student_id: int) -> dict:
    """
    Compute per-student environmental correlation (Sleep & Stress vs accuracy).
    Filters the join to only that student's test sessions.
    """
    from scipy.stats import pearsonr

    conn = sqlite3.connect("student_helper.db")
    query = """
        SELECT
            A.Test_ID,
            AVG(A.Outcome) AS Session_Accuracy,
            B.Sleep_Hours,
            B.Stress_Level
        FROM Academic_Performance_Log A
        JOIN Behavioural_Log B ON A.Test_ID = B.Test_ID
        WHERE A.Student_ID = ?
        GROUP BY A.Test_ID
    """
    df = pd.read_sql_query(query, conn, params=(student_id,))
    conn.close()

    results = {}
    if len(df) < 2:
        return results

    df_sleep = df.dropna(subset=["Sleep_Hours", "Session_Accuracy"])
    if len(df_sleep) >= 2:
        r, p = pearsonr(df_sleep["Sleep_Hours"], df_sleep["Session_Accuracy"])
        results["Sleep"] = {"r": round(r, 3), "p": round(p, 3)}

    df_stress = df.dropna(subset=["Stress_Level", "Session_Accuracy"])
    if len(df_stress) >= 2:
        r, p = pearsonr(df_stress["Stress_Level"], df_stress["Session_Accuracy"])
        results["Stress"] = {"r": round(r, 3), "p": round(p, 3)}

    return results


def run_diagnostics():
    """
    The Final Glue: diagnostics.py
    Runs all modules and generates a consolidated report for EACH student.
    """
    print("-" * 50)
    print("STARTING STUDENT DIAGNOSTIC SUITE (PHASE 2)")
    print("-" * 50)

    # 1. Run Weakness Index Update (covers all students in one pass)
    compute_weakness()

    # 2. Run shared modules (kurtosis is topic-level, not per student)
    kurtosis_results  = analyze_kurtosis()
    knowledge_graph   = build_knowledge_graph()

    # 3. Fetch all students
    conn = sqlite3.connect("student_helper.db")
    students = pd.read_sql_query(
        "SELECT Student_ID, Student_Name FROM Students ORDER BY Student_ID", conn
    )
    profile_all = pd.read_sql_query(
        """
        SELECT Student_ID, Topic_Tag, Average_Accuracy, Weakness_Index
        FROM Student_Profile
        ORDER BY Student_ID, Weakness_Index DESC
        """,
        conn,
    )
    conn.close()

    if profile_all.empty:
        print("Error: No profile data found. Run seed_data.py first.")
        return

    # 4. Print a report for every student
    for _, student_row in students.iterrows():
        sid  = int(student_row["Student_ID"])
        name = student_row["Student_Name"]

        student_profile = profile_all[profile_all["Student_ID"] == sid]
        if student_profile.empty:
            continue

        # Weakest topic = highest Weakness_Index for this student
        weakest_row   = student_profile.iloc[0]
        weakest_topic = weakest_row["Topic_Tag"]

        print("\n" + "=" * 40)
        print(f"   DIAGNOSTIC REPORT - {name} (ID: {sid})")
        print("=" * 40 + "\n")

        print(f"Primary Focus Area: {weakest_topic}")
        print(f"   - Weakness Index : {weakest_row['Weakness_Index']:.3f}")
        print(f"   - Accuracy       : {weakest_row['Average_Accuracy'] * 100:.1f}%")

        # Kurtosis / diagnosis label for the weakest topic
        k_data = kurtosis_results.get(weakest_topic, {"Label": "N/A"})
        print(f"   - Diagnosis      : {k_data['Label']}")

        # Per-student lifestyle correlations
        correlation_results = get_student_correlation(sid)
        if correlation_results:
            print("\nLifestyle Correlation Summary:")
            for factor, data in correlation_results.items():
                level    = "Positive" if data["r"] > 0 else "Negative"
                strength = "Significant" if abs(data["r"]) > 0.5 else "Moderate"
                print(f"   - {factor}: {strength} ({level}) correlation with performance (r={data['r']})")

        # Knowledge-graph root causes
        roots = get_root_causes(knowledge_graph, weakest_topic)
        if roots:
            print(f"\nRoot Prerequisites to review for {weakest_topic}:")
            for root in roots:
                print(f"   - {root}")

    print("\n" + "-" * 50)
    print("Diagnostic Scan Complete.")
    print("-" * 50)


if __name__ == "__main__":
    run_diagnostics()
