import sqlite3
import pandas as pd
import numpy as np

DB_NAME = "student_helper.db"

class PreprocessingPipeline:
    def __init__(self, db_path=DB_NAME):
        self.db_path = db_path

    def load_data(self):
        """Pulls raw data from SQLite into DataFrames."""
        conn = sqlite3.connect(self.db_path)
        academic = pd.read_sql_query("SELECT * FROM Academic_Performance_Log", conn)
        behavioural = pd.read_sql_query("SELECT * FROM Behavioural_Log", conn)
        conn.close()
        return academic, behavioural

    def detect_lucky_guesses(self, df):
        """
        Step 1: IQR Guess Detection.
        Flags correct answers that were completed suspiciously fast based on difficulty level.
        """
        df = df.copy()
        df["Is_Lucky_Guess"] = 0  # Default to 'Not a guess'

        for difficulty in df["Difficulty_Level"].unique():
            # We only calculate the 'normal' threshold using CORRECT answers
            subset = df[(df["Difficulty_Level"] == difficulty) & (df["Outcome"] == 1)]

            if len(subset) >= 4:  # Statistical guardrail: need enough points for IQR
                q1 = subset["Time_Spent_Seconds"].quantile(0.25)
                q3 = subset["Time_Spent_Seconds"].quantile(0.75)
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr

                # Condition: Correct answer AND Time spent is below the lower bound
                mask = (df["Difficulty_Level"] == difficulty) & \
                       (df["Outcome"] == 1) & \
                       (df["Time_Spent_Seconds"] < lower_bound)
                
                df.loc[mask, "Is_Lucky_Guess"] = 1
        
        # Hard Floor Catch: Outliers can distort IQR bounds into negative numbers.
        # Any correct answer faster than 2.0 seconds is a guaranteed guess.
        hard_floor_mask = (df["Outcome"] == 1) & (df["Time_Spent_Seconds"] < 2.0)
        df.loc[hard_floor_mask, "Is_Lucky_Guess"] = 1

        return df

    def scale_metrics(self, df):
        """
        Step 2 & 3: Normalization and Standardization.
        Prepares Time_Spent_Seconds for future ML processing.
        """
        df = df.copy()
        
        # Min-Max Normalization (Scale: 0 to 1)
        t_min, t_max = df["Time_Spent_Seconds"].min(), df["Time_Spent_Seconds"].max()
        if t_max != t_min:
            df["Time_Norm"] = (df["Time_Spent_Seconds"] - t_min) / (t_max - t_min)
        else:
            df["Time_Norm"] = 0

        # Z-Score Standardization (Mean=0, Std=1)
        t_mean, t_std = df["Time_Spent_Seconds"].mean(), df["Time_Spent_Seconds"].std()
        if t_std > 0:
            df["Time_Z"] = (df["Time_Spent_Seconds"] - t_mean) / t_std
        else:
            df["Time_Z"] = 0
            
        return df

    def impute_behavioural(self, df):
        """
        Step 4: Targeted Mean Imputation.
        Only flags 'Is_Imputed' for the specific rows that were missing data.
        """
        df = df.copy()
        mask = df["Sleep_Hours"].isna()
        
        if mask.any():
            mean_sleep = df["Sleep_Hours"].mean()
            # If all sleep hours are missing, default to 7 hours rather than NaN
            if pd.isna(mean_sleep):
                mean_sleep = 7.0
            df.loc[mask, "Sleep_Hours"] = mean_sleep
            df.loc[mask, "Is_Imputed"] = 1 # Targeted flagging
            
        return df

    def save_to_db(self, acad_df, beh_df):
        """Writes processed flags and imputed values back to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Update Academic Flags
        for _, row in acad_df.iterrows():
            cursor.execute("""
                UPDATE Academic_Performance_Log 
                SET Is_Lucky_Guess = ? 
                WHERE Log_ID = ?
            """, (int(row["Is_Lucky_Guess"]), int(row["Log_ID"])))

        # Update Behavioural Data (Imputed values and flags)
        for _, row in beh_df.iterrows():
            is_imputed = int(row["Is_Imputed"]) if pd.notna(row.get("Is_Imputed")) else 0
            sleep_hours = float(row["Sleep_Hours"]) if pd.notna(row.get("Sleep_Hours")) else None
            
            cursor.execute("""
                UPDATE Behavioural_Log 
                SET Sleep_Hours = ?, Is_Imputed = ? 
                WHERE Session_ID = ?
            """, (sleep_hours, is_imputed, int(row["Session_ID"])))

        conn.commit()
        conn.close()

    def run(self):
        """Executes the full pipeline."""
        print("Loading data...")
        acad, beh = self.load_data()

        print("Detecting lucky guesses (IQR)...")
        acad = self.detect_lucky_guesses(acad)

        print("Scaling time metrics (Min-Max & Z-Score)...")
        acad = self.scale_metrics(acad)

        print("Imputing missing behavioural data...")
        beh = self.impute_behavioural(beh)

        print("Saving processed results to database...")
        self.save_to_db(acad, beh)
        
        print("Preprocessing Phase 1 Complete!")

if __name__ == "__main__":
    pipeline = PreprocessingPipeline()
    pipeline.run()
