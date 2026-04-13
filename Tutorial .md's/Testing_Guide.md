# AEGIS-MIND: Full Testing Reset Guide

To securely wipe the slate clean and test all modules end-to-end (including Phase 1, 2, 3, AND 4), follow these robust command-line steps. This ensures no residual models or graphs interfere with your next run.

## Step 1: Nuke the Old Data
To start from complete basics, you should destroy the old SQLite file and the Chroma vector database. Run these commands carefully inside your `StudentHelper` directory:

### On Windows PowerShell:
```powershell
Remove-Item -Path "student_helper.db" -Force -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "chroma_db\" -ErrorAction SilentlyContinue
```

## Step 2: Initialize & Seed Baseline Data
Because the diagnostic engine (`diagnostics.py`) and behavioral history (`weakness_index.py`) mathematically require *some* past history to compute correlations (like Stress vs Sleep), you must seed the baseline again.

Run this using your environment's Python:
```powershell
.venv\Scripts\python.exe seed_data.py
```
> [!NOTE]
> `seed_data.py` automatically fires `init_db()` for you, so the SQLite schema will instantly recreate perfectly, immediately populating with baseline statistics so the agent can accurately find a "Weakest Topic."

## Step 3: Test With Your Custom PDF
I’ve updated `phase4/agent.py` to make testing your own PDFs incredibly easy.

1. **Open** `phase4/agent.py` in your code editor.
2. Scroll to the very bottom block (`if __name__ == "__main__":`).
3. Comment out the default line (`run_agent_session(STUDENT_ID)`).
4. Uncomment the variables for `CUSTOM_TOPIC` and `MY_PDF_PATH`.
5. Point them to your document! 

**Example Modification:**
```python
if __name__ == "__main__":
    STUDENT_ID = 1
    
    # Unleash your custom PDF!
    CUSTOM_TOPIC = "Advanced Calculus"
    MY_PDF_PATH = "C:/absolute/path/to/my_calculus_notes.pdf"
    
    run_agent_session(STUDENT_ID, custom_topic=CUSTOM_TOPIC, custom_pdf_path=MY_PDF_PATH)
```

## Step 4: Run the Agent
With your files pointed safely at your PDF, simply orchestrate the session:

```powershell
.venv\Scripts\python.exe phase4/agent.py
```

### What You Should Expect to See:
1. It acknowledges your custom topic, "Advanced Calculus".
2. It parses your *actual* PDF using the Phase 3 chunkers.
3. It asks Gemini 1.5 Flash to generate MCQs accurately based purely on the text inside *your* PDF.
4. It quizzes you in the terminal.
5. It runs Phase 1 Preprocessing to standardize your runtime.
6. It runs Phase 2 Diagnostics and safely displays **only** Aditya's updated profile.
