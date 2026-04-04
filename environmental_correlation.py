import sqlite3
import pandas as pd
from scipy.stats import pearsonr

def analyze_environmental_correlation():
    """
    Module 3: Environmental Correlation Analysis.
    Correlates lifestyle factors (Sleep, Stress) with academic performance.
    """
    conn = sqlite3.connect("student_helper.db")
    
    # 1. Join academic logs with behavioural logs on Test_ID
    # We aggregate performance per test (session)
    query = """
    SELECT 
        A.Test_ID, 
        AVG(A.Outcome) as Session_Accuracy, 
        B.Sleep_Hours, 
        B.Stress_Level
    FROM Academic_Performance_Log A
    JOIN Behavioural_Log B ON A.Test_ID = B.Test_ID
    GROUP BY A.Test_ID
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    results = {}
    
    # Needs at least 2 data points for correlation
    if len(df) < 2:
        print("⚠️ Module 3: Not enough session data to compute correlation.")
        return results

    # 2. Compute Pearson Correlation for Sleep vs Accuracy
    # Handle NaN cases if any (though preprocessing should have imputed them)
    df_sleep = df.dropna(subset=['Sleep_Hours', 'Session_Accuracy'])
    if len(df_sleep) >= 2:
        r_sleep, p_sleep = pearsonr(df_sleep['Sleep_Hours'], df_sleep['Session_Accuracy'])
        results['Sleep'] = {"r": round(r_sleep, 3), "p": round(p_sleep, 3)}
    
    # 3. Compute Pearson Correlation for Stress vs Accuracy
    df_stress = df.dropna(subset=['Stress_Level', 'Session_Accuracy'])
    if len(df_stress) >= 2:
        r_stress, p_stress = pearsonr(df_stress['Stress_Level'], df_stress['Session_Accuracy'])
        results['Stress'] = {"r": round(r_stress, 3), "p": round(p_stress, 3)}

    print("✅ Module 3: Environmental Correlation Analysis Complete.")
    return results

if __name__ == "__main__":
    res = analyze_environmental_correlation()
    for factor, stat in res.items():
        print(f"{factor} vs Accuracy: r = {stat['r']} (p = {stat['p']})")
