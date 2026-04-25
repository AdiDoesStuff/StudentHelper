import sqlite3

def display_all():
    conn = sqlite3.connect("student_helper.db")
    cursor = conn.cursor()
    
    # We will grab all our main tables
    tables = [
        "Students",
        "Student_Profile",
        "Behavioural_Log",
        "Academic_Performance_Log"
    ]
    
    for table_name in tables:
        print(f"\n{'='*80}")
        print(f" TABLE: {table_name}")
        print(f"{'='*80}")
        
        try:
            # First try using pandas for beautiful tabular printing
            import pandas as pd
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
            
            if df.empty:
                 print("(Table is currently empty)")
            else:
                 print(df.to_string(index=False))
                 
        except ImportError:
            # Fallback to pure Python text formatting if Pandas isn't pip installed yet
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            
            if not rows:
                 print("(Table is currently empty)")
            else:
                # Dynamically get column headers
                col_names = [description[0] for description in cursor.description]
                header = " | ".join(col_names)
                print(header)
                print("-" * len(header))
                for row in rows:
                    print(" | ".join(str(item) for item in row))
                    
    conn.close()

if __name__ == "__main__":
    display_all()
