import sys
import os
import time
import datetime
import sqlite3

# Add root directory to path so core imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.generator.pipeline import run_pipeline
from core.runner.question_store import store_questions
from core.runner.session_logger import create_session, log_answers
from core.runner.test_runner import run_test
from core.analytics.preprocessing import PreprocessingPipeline
from core.analytics.diagnostics import run_diagnostics

def get_weakest_topic(student_id: int) -> str:
    conn = sqlite3.connect("student_helper.db")
    cursor = conn.cursor()
    
    # Calculate date 3 days ago
    three_days_ago = (datetime.date.today() - datetime.timedelta(days=3)).isoformat()
    
    cursor.execute('''
        SELECT Topic_Tag, Weakness_Index, Last_Tested_Date
        FROM Student_Profile
        WHERE Student_ID = ?
        ORDER BY Weakness_Index DESC
    ''', (student_id,))
    
    topics = cursor.fetchall()
    conn.close()
    
    if not topics:
        print(f"No topics found for Student_ID {student_id}")
        sys.exit(1)
        
    # Filter out topics tested in the last 3 days
    for t in topics:
        topic_tag, weakness_index, last_tested = t
        if last_tested is None or last_tested <= three_days_ago:
            return topic_tag
            
    # If all were tested recently, fallback to the first (highest weakness)
    return topics[0][0]

def collect_pre_session_vitals() -> tuple:
    print("\n[AEGIS-MIND: Pre-session data collection]")
    print("Capturing this information helps us understand environmental impacts on your performance.")
    
    while True:
        try:
            sleep_input = input("How many hours did you sleep last night? (0-24): ").strip()
            sleep_hours = float(sleep_input)
            if 0 <= sleep_hours <= 24:
                break
            print("Please enter a valid number between 0 and 24.")
        except ValueError:
            print("Please enter a valid number.")
            
    while True:
        try:
            stress_input = input("Rate your current stress level (1-10): ").strip()
            stress_level = int(stress_input)
            if 1 <= stress_level <= 10:
                break
            print("Please enter an integer between 1 and 10.")
        except ValueError:
            print("Please enter a valid integer.")
            
    return sleep_hours, stress_level

def run_agent_session(student_id: int, custom_topic: str = None, custom_pdf_path: str = None) -> None:
    # STEP 1 - Greet student
    conn = sqlite3.connect("student_helper.db")
    cursor = conn.cursor()
    cursor.execute("SELECT Student_Name FROM Students WHERE Student_ID = ?", (student_id,))
    student_row = cursor.fetchone()
    conn.close()
    
    student_name = student_row[0] if student_row else "Student"
    print(f"\nWelcome back to AEGIS-MIND, {student_name}!")
    
    # STEP 2 - Collect vitals
    sleep_hours, stress_level = collect_pre_session_vitals()
    
    # STEP 3 - Determine weakest topic
    topic_tag = custom_topic if custom_topic else get_weakest_topic(student_id)
    print(f"\nToday's focus topic: {topic_tag}")
    
    # Dynamically generate or select PDF based on the topic
    if custom_pdf_path:
        pdf_path = custom_pdf_path
        if not os.path.exists(pdf_path):
            print(f"Error: Custom PDF not found at {pdf_path}")
            return
    else:
        pdf_filename = f"test_{topic_tag.lower().replace(' ', '_')}.pdf"
        pdf_path = os.path.join("core", "generator", pdf_filename)
        
        if not os.path.exists(pdf_path):
            print(f"Generating notes PDF for {topic_tag}...")
            import fitz
            topic_contents = {
                "Quantum Gates": "Quantum gates are simple quantum circuits operating on a small number of qubits. They are the building blocks of quantum circuits, similar to classical logic gates. The Pauli-X gate acts as a quantum NOT gate, and the Hadamard gate creates superposition.",
                "Thermodynamics": "Thermodynamics deals with heat, work, and temperature, and their relation to energy and entropy. The first law concerns the conservation of energy. The second law introduces entropy, stating that the total entropy of an isolated system can never decrease.",
                "Kinematics": "Kinematics describes the motion of points, bodies, and systems without considering the forces causing them to move. Key parameters include velocity (rate of change of displacement), acceleration (rate of change of velocity), displacement, and time.",
                "Linear Algebra": "Linear algebra concerns linear equations, linear maps, and their representations in vector spaces via matrices. Key concepts include vectors, matrices, determinants, eigenvalues, and eigenvectors. Matrix multiplication allows the composition of linear transformations.",
                "Data Structures": "A data structure is a data organization and storage format enabling efficient access and modification. Examples include arrays (contiguous memory), linked lists (pointers), trees (hierarchical), and graphs (nodes and edges). They are essential for designing efficient algorithms.",
                "Electrostatics": "Electrostatics studies stationary electric charges. Coulomb's Law states that the electrostatic force between two point charges is directly proportional to the product of their magnitudes and inversely proportional to the square of the distance between them."
            }
            doc = fitz.open()
            page = doc.new_page()
            content = topic_contents.get(topic_tag, f"{topic_tag} is a crucial area of study. The core concepts involve understanding the foundational principles, the related equations, and applying them correctly in structured problems.")
            page.insert_text((50, 50), content, fontsize=12)
            doc.save(pdf_path)
            doc.close()
    
    # STEP 4 - Generate unique Test_ID
    test_id = int(time.time())
    
    # STEP 5 - Create session
    create_session(student_id, test_id, sleep_hours, stress_level)
    print("Session created in database.")
    
    # STEP 6 - Run Phase 3 RAG pipeline
    print(f"\nAnalyzing notes for {topic_tag} via Gemini...")
    questions = run_pipeline(pdf_path, topic_tag)
    
    if not questions:
        print("Failed to generate questions. Aborting session.")
        return
        
    # STEP 7 - Store questions
    inserted = store_questions(questions, student_id, test_id, topic_tag)
    print(f"Stored {inserted} questions in database.")
    
    # STEP 8 - Administer test
    answers = run_test(student_id, test_id, topic_tag)
    
    # STEP 9 - Log answers
    log_answers(answers)
    
    # STEP 10 - Run preprocessing
    print("\nRunning preprocessing pipeline...")
    pipeline = PreprocessingPipeline()
    pipeline.run()
    
    # STEP 11 - Run diagnostics
    print("\nRunning diagnostics...")
    run_diagnostics(student_id)
    
    # STEP 12 - Print closing message
    print("\nSession complete. Your diagnostic profile has been updated.")

if __name__ == "__main__":
    STUDENT_ID = 1
    
    # DEFAULT BEHAVIOR: Automatically find weakest topic and generate a dummy PDF.
    # run_agent_session(STUDENT_ID)
    
    # CUSTOM TESTING BEHAVIOR: 
    # Use these if you want to test the system with YOUR OWN uploaded PDF.
    # Specify the topic name it relates to, and the absolute or relative path to your PDF.
    #
    # Uncomment the following to test with a custom PDF:
    CUSTOM_TOPIC = "MAOM"
    MY_PDF_PATH = "C:\\Users\\Aditya Vineeth\\Desktop\\COLLEGE DOCS\\FULL SEM 2\\PROJECTS\\AI-ML\\StudentHelper\\CB.AI.U4QTS25002 - MAOM - Compasssionate Project - Abstract (1).pdf"
    run_agent_session(STUDENT_ID, custom_topic=CUSTOM_TOPIC, custom_pdf_path=MY_PDF_PATH)
    
    # (Leaving default enabled for now until you customize it)
    # run_agent_session(STUDENT_ID)
