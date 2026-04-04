import sqlite3
import pandas as pd
from weakness_index import compute_weakness
from kurtosis_analysis import analyze_kurtosis
from environmental_correlation import analyze_environmental_correlation
from knowledge_graph import build_knowledge_graph, get_root_causes

def run_diagnostics():
    """
    The Final Glue: diagnostics.py
    Runs all modules and generates a consolidated report.
    """
    print("-" * 50)
    print("🚀 STARTING STUDENT DIAGNOSTIC SUITE (PHASE 2)")
    print("-" * 50)

    # 1. Run Weakness Index Update
    # This updates the DB persistent state
    compute_weakness()

    # 2. Run Other Analysis Modules
    kurtosis_results = analyze_kurtosis()
    correlation_results = analyze_environmental_correlation()
    knowledge_graph = build_knowledge_graph()

    # 3. Pull results from Student_Profile for display
    conn = sqlite3.connect("student_helper.db")
    profile = pd.read_sql_query("""
        SELECT Topic_Tag, Average_Accuracy, Weakness_Index 
        FROM Student_Profile 
        ORDER BY Weakness_Index DESC
    """, conn)
    conn.close()

    if profile.empty:
        print("❌ Error: No profile data found. Run seed_data.py first.")
        return

    # 4. Generate Report Output
    print("\n" + "=" * 30)
    print("      DIAGNOSTIC REPORT")
    print("=" * 30 + "\n")

    weakest_topic = profile.iloc[0]['Topic_Tag']
    print(f"📉 Primary Focus Area: {weakest_topic}")
    print(f"   - Weakness Index: {profile.iloc[0]['Weakness_Index']:.3f}")
    print(f"   - Accuracy: {profile.iloc[0]['Average_Accuracy']*100:.1f}%")

    # 5. Add Kurtosis Labeling
    k_data = kurtosis_results.get(weakest_topic, {"Label": "N/A"})
    print(f"   - Diagnosis: {k_data['Label']}")

    # 6. Correlation Insights
    if correlation_results:
        print("\n🌱 Lifestyle Correlation Summary:")
        for factor, data in correlation_results.items():
            level = "Positive" if data['r'] > 0 else "Negative"
            strength = "Significant" if abs(data['r']) > 0.5 else "Moderate"
            print(f"   - {factor}: {strength} ({level}) correlation with performance (r={data['r']})")

    # 7. Root Cause topics from Knowledge Graph
    roots = get_root_causes(knowledge_graph, weakest_topic)
    if roots:
        print(f"\n🧠 Root Prerequisites to review for {weakest_topic}:")
        for root in roots:
            print(f"   - {root}")

    print("\n" + "-" * 50)
    print("✅ Diagnostic Scan Complete.")
    print("-" * 50)

if __name__ == "__main__":
    run_diagnostics()
