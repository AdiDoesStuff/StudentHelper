import json
import sqlite3
import os
from datetime import datetime, timedelta
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

DB_PATH = "student_helper.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def _extract_json(raw_text: str) -> str:
    text = raw_text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()

def _get_upcoming_test_instances(student_id: int, start_date: datetime, days_ahead: int = 14):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check what schedule templates exist
    cursor.execute("SELECT * FROM Weekly_Test_Schedule WHERE Student_ID = ?", (student_id,))
    schedules = cursor.fetchall()
    
    end_date = start_date + timedelta(days=days_ahead)
    days_map = {
        "Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, 
        "Friday": 4, "Saturday": 5, "Sunday": 6
    }
    
    # Generate instances if they don't exist
    for sched in schedules:
        subject = sched["Subject_Name"]
        day_name = sched["Day_of_Week"]
        target_weekday = days_map.get(day_name, -1)
        
        if target_weekday == -1:
            continue
            
        current_date = start_date
        while current_date <= end_date:
            if current_date.weekday() == target_weekday:
                date_str = current_date.strftime("%Y-%m-%d")
                # check if instance exists
                cursor.execute("""
                    SELECT 1 FROM Test_Instances 
                    WHERE Student_ID = ? AND Subject_Name = ? AND Test_Date = ?
                """, (student_id, subject, date_str))
                
                if not cursor.fetchone():
                    cursor.execute("""
                        INSERT INTO Test_Instances (Student_ID, Subject_Name, Test_Date, Is_Imported)
                        VALUES (?, ?, ?, 0)
                    """, (student_id, subject, date_str))
            current_date += timedelta(days=1)
            
    conn.commit()
    
    # Now fetch all upcoming tests
    cursor.execute("""
        SELECT Instance_ID, Subject_Name, Test_Date, Is_Imported 
        FROM Test_Instances 
        WHERE Student_ID = ? AND Test_Date >= ? AND Test_Date <= ?
        ORDER BY Test_Date ASC
    """, (student_id, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))
    
    tests = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return tests

def generate_study_plan(student_id: int, force_regenerate: bool = False):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    today = datetime.now()
    date_str = today.strftime("%Y-%m-%d")
    
    # 1. Check existing state
    if not force_regenerate:
        cursor.execute("""
            SELECT Plan_JSON, Valid_Until FROM Study_Plan_State
            WHERE Student_ID = ? AND Valid_Until >= ?
            ORDER BY Generated_Date DESC LIMIT 1
        """, (student_id, date_str))
        row = cursor.fetchone()
        if row:
            conn.close()
            return json.loads(row["Plan_JSON"])
            
    # 2. Get upcoming tests (next 2 days)
    upcoming_tests = _get_upcoming_test_instances(student_id, today, days_ahead=2)
    # We still proceed even if tests are empty, because weekends might have no tests and we want revision prompts.
        
    # 3. Get Availability
    cursor.execute("SELECT Day_of_Week, Start_Time, End_Time FROM Study_Availability WHERE Student_ID = ?", (student_id,))
    availability = [dict(row) for row in cursor.fetchall()]
    
    # 3.5 Get Student Accuracy
    cursor.execute("SELECT AVG(Average_Accuracy) as overall_acc FROM Student_Profile WHERE Student_ID = ?", (student_id,))
    acc_row = cursor.fetchone()
    overall_accuracy = round(acc_row["overall_acc"], 2) if acc_row and acc_row["overall_acc"] is not None else 0.0
    
    # 4. Get Weak Topics
    subjects = list(set([t["Subject_Name"] for t in upcoming_tests]))
    if subjects:
        placeholders = ",".join(["?"] * len(subjects))
        cursor.execute(f"""
            SELECT st.Subject_Name, sp.Topic_Tag, sp.Weakness_Index
            FROM Student_Profile sp
            JOIN Syllabus_Topics st ON sp.Topic_Tag = st.Topic_Name
            WHERE sp.Student_ID = ? AND st.Subject_Name IN ({placeholders})
            ORDER BY sp.Weakness_Index DESC
        """, [student_id] + subjects)
        weak_topics = [dict(row) for row in cursor.fetchall()]
    else:
        cursor.execute("""
            SELECT st.Subject_Name, sp.Topic_Tag, sp.Weakness_Index
            FROM Student_Profile sp
            JOIN Syllabus_Topics st ON sp.Topic_Tag = st.Topic_Name
            WHERE sp.Student_ID = ?
            ORDER BY sp.Weakness_Index DESC
            LIMIT 5
        """, (student_id,))
        weak_topics = [dict(row) for row in cursor.fetchall()]
    
    # 5. Build prompt for Groq
    load_dotenv()
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key or groq_key == "your_groq_api_key_here":
        conn.close()
        raise ValueError("GROQ_API_KEY is missing")
        
    try:
        from groq import Groq
    except ImportError:
        conn.close()
        raise ImportError("groq package is not installed.")
        
    client = Groq(api_key=groq_key)
    
    PROMPT_TEMPLATE = """
You are an expert personalized study coach. Write a conversational, focused study plan for the student for just the next 2 days (Today and Tomorrow). 

Current Date and Time: {today}
Student's Current Average Accuracy: {accuracy}%

Here is the student's Study Availability:
{availability}

Here are the Upcoming Tests (Next 2 Days only):
{tests}

Here are the student's weakest topics (higher Weakness_Index means they are weaker and need more focus):
{topics}

Instructions:
1. Write your response directly in natural, conversational Markdown. Do NOT output a JSON array.
2. If there are tests tomorrow, tell the student what subjects they are, acknowledge their availability today, and tell them exactly what weak topics they need to focus on and for how long.
3. Suggest a realistic target score (e.g. 5-10% higher than their current average) to aim for in order to improve their overall grade.
4. If there are NO tests tomorrow, give ONE block of advice for TODAY only. Do NOT break it into a day-by-day schedule. Encourage the student to use their available time today to review past mistakes and practice questions on the weak topics provided below to stay sharp.
5. Keep it concise, motivational, and highly actionable. Don't invent tests that aren't in the list.

Format Example:
"It is currently [Time].
Okay so for tomorrow you have the following tests (and I have analyzed the time that you provided that you will be free today: [Time]):
- **[Subject 1]**: In this subject you have made mistakes in [Topics]. I think it's important you go through these specifically to improve. You should spend [Time] on this.
Overall, try and aim for a [Target]% score to boost your current average of [Accuracy]%. You got this!"
    """
    
    prompt_text = PROMPT_TEMPLATE.format(
        today=datetime.now().strftime("%A, %Y-%m-%d %I:%M %p"),
        accuracy=round(overall_accuracy * 100, 1),
        availability=json.dumps(availability, indent=2),
        tests=json.dumps(upcoming_tests, indent=2),
        topics=json.dumps(weak_topics, indent=2)
    )
    
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt_text}],
        temperature=0.2,
        max_tokens=2000,
    )
    output_text = completion.choices[0].message.content.strip()
    
    plan_data = {"study_plan_markdown": output_text}
        
    # 6. Save State
    valid_until = (today + timedelta(days=7)).strftime("%Y-%m-%d") # Cache for 7 days
    
    cursor.execute("DELETE FROM Study_Plan_State WHERE Student_ID = ?", (student_id,))
    
    cursor.execute("""
        INSERT INTO Study_Plan_State (Student_ID, Generated_Date, Plan_JSON, Valid_Until)
        VALUES (?, ?, ?, ?)
    """, (student_id, date_str, json.dumps(plan_data), valid_until))
    
    conn.commit()
    conn.close()
    
    return plan_data
