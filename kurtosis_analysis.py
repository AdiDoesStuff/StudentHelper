from scipy.stats import kurtosis
import sqlite3
import pandas as pd

def analyze_kurtosis():
    """
    Module 2: Kurtosis Analysis.
    Identifies if performance issues are systematic (General Weakness) 
    or due to specific mental blocks.
    """
    conn = sqlite3.connect("student_helper.db")
    df = pd.read_sql_query("""
        SELECT Topic_Tag, Time_Spent_Seconds, Difficulty_Level 
        FROM Academic_Performance_Log
    """, conn)
    
    # 1. Compute T_adjusted (Time - Mean for that Difficulty level)
    # This ensures a 50s "Hard" question isn't penalized like a 50s "Easy" one.
    means = df.groupby('Difficulty_Level')['Time_Spent_Seconds'].transform('mean')
    df['T_adj'] = df['Time_Spent_Seconds'] - means

    # 2. Compute Kurtosis per Topic
    results = {}
    for topic in df['Topic_Tag'].unique():
        topic_times = df[df['Topic_Tag'] == topic]['T_adj']
        
        # Statistical minimum check: kurtosis needs some variance/data
        if len(topic_times) >= 4: 
            # fisher=True returns excess kurtosis (Normal = 0)
            k_val = kurtosis(topic_times, fisher=True)
            
            # Threshold: > 1 indicates heavy tails (Specific Blocks/Outliers)
            label = "Specific Block" if k_val > 1 else "General Weakness"
            results[topic] = {
                "Kurtosis": round(k_val, 2),
                "Label": label
            }
        else:
            results[topic] = {
                "Kurtosis": None,
                "Label": "Insufficient Data"
            }

    conn.close()
    print("✅ Module 2: Kurtosis Analysis Complete.")
    return results

if __name__ == "__main__":
    res = analyze_kurtosis()
    for topic, data in res.items():
        print(f"{topic}: {data['Label']} (K={data['Kurtosis']})")
