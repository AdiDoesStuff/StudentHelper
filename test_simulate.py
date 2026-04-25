import sqlite3
from core.generator.test_builder import build_test

def simulate():
    try:
        subject = "User Interface Design"
        topics = ["Introduction to Java Script"]
        
        print(f"Testing with Subject: {subject}, Topics: {topics}")
        
        test_id = build_test(
            student_id=1,
            subject=subject,
            topics=topics,
            num_questions=2,
            sleep_hours=8.0,
            stress_level=5
        )
        print("Test generated successfully. Test ID:", test_id)
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simulate()
