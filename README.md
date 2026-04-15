# AEGIS-MIND (StudentHelper)

AEGIS-MIND is an AI-assisted adaptive learning and diagnostics platform built around four connected layers:
- student session logging,
- statistical diagnostics,
- RAG-based question generation from uploaded notes,
- and a Streamlit interface for end-to-end use.

The system tracks test behavior over time, computes topic-level weakness, correlates lifestyle factors with performance, and uses prerequisite chains derived from syllabus text to suggest root-cause revision paths.

---

## Table of Contents
- [What This Project Does](#what-this-project-does)
- [Core Workflow (End-to-End)](#core-workflow-end-to-end)
- [Tech Stack](#tech-stack)
- [Repository Structure](#repository-structure)
- [Database Design](#database-design)
- [Analytics and Diagnostic Logic](#analytics-and-diagnostic-logic)
- [RAG Pipeline (Phase 3)](#rag-pipeline-phase-3)
- [Agent/Test Orchestration (Phase 4)](#agenttest-orchestration-phase-4)
- [Streamlit Pages and UX Flow](#streamlit-pages-and-ux-flow)
- [Syllabus Mapping and Knowledge Graph](#syllabus-mapping-and-knowledge-graph)
- [Setup and Installation](#setup-and-installation)
- [How to Run](#how-to-run)
- [Data Reset / Fresh Testing](#data-reset--fresh-testing)
- [Troubleshooting](#troubleshooting)
- [Known Limitations and Current Design Constraints](#known-limitations-and-current-design-constraints)
- [Security and Privacy Notes](#security-and-privacy-notes)
- [Future Improvements (Recommended)](#future-improvements-recommended)
- [License](#license)

---

## What This Project Does

AEGIS-MIND focuses on identifying *why* a student is weak in a topic, not only *whether* they are weak.

At a high level, it:
1. captures behavioral context per test (sleep, stress),
2. asks generated topic-targeted MCQs,
3. logs answer outcomes and response time,
4. preprocesses data (outlier-style guess detection + imputation),
5. computes multi-module diagnostics,
6. displays insights in dashboard and report form.

The project currently uses a **single-student Streamlit mode** (`student_id = 1` in `app.py`), while the schema supports multiple students.

---

## Core Workflow (End-to-End)

1. Open app via `streamlit run app.py`.
2. Enter pre-session vitals (sleep and stress), upload PDF notes, and enter a `Topic_Tag`.
3. Phase 3 pipeline:
   - extract text from PDF,
   - chunk text,
   - embed chunks into Chroma,
   - retrieve top relevant chunks by topic,
   - generate MCQs via Gemini.
4. Store generated questions in SQLite for that test session.
5. Take test in Streamlit page.
6. On completion:
   - answers are logged,
   - preprocessing pipeline runs,
   - diagnostics suite runs,
   - report/dashboard reflect updated profile.

---

## Tech Stack

### Language and App Framework
- Python
- Streamlit (multipage app)

### Data and Analytics
- SQLite
- pandas, numpy, scipy
- networkx
- plotly

### AI / RAG
- LangChain core utilities
- LangChain text splitters
- LangChain Chroma integration
- LangChain Google GenAI integration
- Gemini models (embeddings + question generation)
- Chroma persistent local vector store

### PDF Processing
- PyMuPDF (`fitz`)

### Environment
- `python-dotenv`

Dependency versions are pinned in `requirements.txt`.

---

## Repository Structure

```text
StudentHelper/
├── app.py
├── database_init.py
├── seed_data.py
├── preprocessing.py
├── diagnostics.py
├── weakness_index.py
├── kurtosis_analysis.py
├── environmental_correlation.py
├── knowledge_graph.py
├── syllabus_parser.py
├── displayall.py
├── electrostatics_summary.py
├── requirements.txt
├── README.md
├── pages/
│   ├── 1_Dashboard.py
│   ├── 2_Upload_and_Generate.py
│   ├── 3_Take_Test.py
│   ├── 4_Diagnostic_Report.py
│   └── 5_Syllabus_Mapping.py
├── phase3/
│   ├── ocr_extractor.py
│   ├── chunker.py
│   ├── embedder.py
│   ├── rag_engine.py
│   ├── question_generator.py
│   ├── pipeline.py
│   ├── generate_test_pdf.py
│   └── test_embed.py
├── phase4/
│   ├── agent.py
│   ├── test_runner.py
│   ├── session_logger.py
│   └── question_store.py
└── Tutorial .md's/
    ├── Testing_Guide.md
    └── hereyougo.md
```

---

## Database Design

Database file: `student_helper.db` (created automatically if missing).

### 1) `Students`
- `Student_ID` (PK)
- `Student_Name`

### 2) `Student_Profile`
Primary key: (`Student_ID`, `Topic_Tag`)
- stores weak-topic profile state:
  - `Weakness_Index`
  - `Concept_Weightage`
  - `Last_Tested_Date`
  - `Session_Cluster_State`
  - `Total_Sessions`
  - `Average_Accuracy`
  - `Cumulative_Time_Spent`

### 3) `Behavioural_Log`
- per session metadata:
  - `Session_ID` (PK, autoincrement)
  - `Student_ID`
  - `Test_ID` (unique)
  - `Sleep_Hours`
  - `Stress_Level` (1-10)
  - `Session_Date`
  - `Session_Duration_Seconds`
  - `Is_Imputed`

### 4) `Questions`
- generated MCQs tied to session and topic:
  - `Question_ID` (PK)
  - `Student_ID`
  - `Test_ID`
  - `Topic_Tag`
  - `Question_Text`
  - `Options` (JSON string)
  - `Correct_Answer` (`A/B/C/D`)
  - `Difficulty_Level` (1/2/3)
  - `Was_Asked` (0/1)

### 5) `Academic_Performance_Log`
- per attempted question:
  - `Log_ID` (PK)
  - `Student_ID`, `Test_ID`, `Topic_Tag`, `Question_ID`
  - `Outcome` (0/1)
  - `Time_Spent_Seconds`
  - `Difficulty_Level`
  - `Time_of_Day`
  - `Test_Sequence_Number`
  - `Is_Lucky_Guess`

### 6) `Syllabus_Topics`
Primary key: (`Subject_Name`, `Unit_Number`, `Topic_Order`)
- ordered topic list used to derive prerequisite edges.

---

## Analytics and Diagnostic Logic

### Weakness Index (`weakness_index.py`)
Formula:
`Weakness_Index = (1 - Accuracy) * Concept_Weightage`

Accuracy is computed from `Academic_Performance_Log`, excluding rows where `Is_Lucky_Guess = 1`.

### Kurtosis Analysis (`kurtosis_analysis.py`)
- Adjusts response time by per-difficulty mean (`T_adj`).
- Computes kurtosis per topic (requires at least 4 points).
- Labels:
  - `Specific Block` if kurtosis > 1,
  - `General Weakness` otherwise,
  - `Insufficient Data` if too few points.

### Environmental Correlation (`environmental_correlation.py` / `diagnostics.py`)
- Computes session-level average accuracy.
- Calculates Pearson correlations:
  - Sleep vs accuracy
  - Stress vs accuracy

### Knowledge Graph Root Causes (`knowledge_graph.py`)
- Builds directed graph from syllabus-derived prerequisite edges.
- Root causes for a weak topic = graph ancestors of that topic.

### Orchestration (`diagnostics.py`)
`run_diagnostics()` coordinates:
1. weakness computation,
2. kurtosis module,
3. graph build,
4. student-wise printed report with primary focus area and roots.

---

## RAG Pipeline (Phase 3)

### `phase3/ocr_extractor.py`
- Reads uploaded PDF page-by-page with PyMuPDF.

### `phase3/chunker.py`
- Splits extracted text into overlapping chunks (`chunk_size=2000`, `chunk_overlap=250`).
- Stores chunk metadata: page number + `Topic_Tag`.

### `phase3/embedder.py`
- Loads `GEMINI_API_KEY` from `.env`.
- Uses Gemini embedding model (`models/gemini-embedding-001`).
- Persists vectors to local `./chroma_db`, collection `student_helper_rag`.

### `phase3/rag_engine.py`
- Retrieves top-k chunks (default `k=5`) filtered by current `Topic_Tag`.

### `phase3/question_generator.py`
- Uses Gemini chat model (`gemini-2.5-flash-lite`) with strict JSON output instructions.
- Normalizes common malformed outputs (key aliases, answer formats, difficulty coercion).
- Validates and drops invalid questions.
- Returns only normalized question objects.

### `phase3/pipeline.py`
Single orchestrator function:
`run_pipeline(pdf_path, topic_tag, generate_count=5)`

---

## Agent/Test Orchestration (Phase 4)

### `phase4/session_logger.py`
- Creates behavioral session row.
- Logs answer-level data to academic table.
- Updates `Session_Duration_Seconds`.
- Increments `Student_Profile.Total_Sessions` and updates `Last_Tested_Date`.

### `phase4/question_store.py`
- Inserts generated question payloads into `Questions`.

### `phase4/test_runner.py`
- Terminal quiz loop for unanswered questions.
- Captures timing and correctness.
- Marks `Was_Asked`.

### `phase4/agent.py`
- Can run complete terminal-based session:
  1. welcome + vitals,
  2. weakest-topic detection (with 3-day recency filter),
  3. PDF selection (custom or generated fallback),
  4. phase3 pipeline,
  5. test,
  6. logging + preprocessing + diagnostics.

---

## Streamlit Pages and UX Flow

### `app.py`
- Sets app config.
- Initializes DB via `init_db()`.
- Enforces single-student session (`student_id = 1`).

### `pages/1_Dashboard.py`
- Recommended focus topic (highest weakness not recently tested).
- Weakness bar chart by topic.
- detailed profile table.
- aggregate session metrics.

### `pages/2_Upload_and_Generate.py`
- Collects sleep/stress sliders.
- Uploads PDF + topic tag.
- Creates session and runs RAG generation.
- Stores generated questions.

### `pages/3_Take_Test.py`
- Loads unasked questions for current test.
- Handles answer submission and per-question timing.
- On completion: logs answers, runs preprocessing + diagnostics, shows score and breakdown.

### `pages/4_Diagnostic_Report.py`
- Weakness ranking list.
- Kurtosis interpretation text.
- Sleep/stress correlation metrics.
- Knowledge-graph prerequisite recommendations.
- session accuracy trend chart.

### `pages/5_Syllabus_Mapping.py`
- Parses syllabus text into ordered topics per unit.
- Saves mapping to DB.
- Shows stored topics and derived prerequisite edges.

---

## Syllabus Mapping and Knowledge Graph

`syllabus_parser.py` provides robust syllabus parsing with:
- unit-header detection (`Unit`/`Module`, Arabic + Roman numerals),
- whitespace normalization,
- broken-hyphen repair,
- lexical hyphen protection (`object-oriented`, `built-in`, etc.),
- boundary sentinel injection for topic splitting,
- fragment re-merging for compound names (`Gram-Schmidt`, `Floyd-Warshall`, etc.),
- fine-grained sentence/comma splitting.

Public APIs:
- `parse_unit_text(unit_text) -> list[str]`
- `parse_syllabus_text(raw_text) -> dict[int, list[str]]`
- `store_syllabus(subject_name, units, db_path=...)`
- `load_syllabus_edges(db_path=...) -> list[(prereq, target)]`

Prerequisite edges are generated from consecutive topic order **within each unit**.

---

## Setup and Installation

### Prerequisites
- Python 3.10+ recommended
- Internet access for Gemini API calls

### 1) Clone and enter project
```bash
git clone <your-repo-url>
cd StudentHelper
```

### 2) Create virtual environment
```bash
python -m venv .venv
```

Activate:
- Windows PowerShell:
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```
- Windows CMD:
  ```cmd
  .venv\Scripts\activate.bat
  ```

### 3) Install dependencies
```bash
pip install -r requirements.txt
```

### 4) Configure environment variables
Create `.env` in project root:

```env
GEMINI_API_KEY=your_actual_api_key_here
```

---

## How to Run

### Primary method: Streamlit app
```bash
streamlit run app.py
```

### Optional: Manual terminal workflow
```bash
python database_init.py
python seed_data.py
python preprocessing.py
python diagnostics.py
```

### Optional: Run only Phase 3 pipeline directly
```bash
python phase3/pipeline.py <pdf_path> <topic_tag>
```

### Optional: Run full terminal agent flow
```bash
python phase4/agent.py
```

---

## Data Reset / Fresh Testing

To fully reset:

### Windows PowerShell
```powershell
Remove-Item -Path "student_helper.db" -Force -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "chroma_db\" -ErrorAction SilentlyContinue
```

Then reseed:
```bash
python seed_data.py
```

---

## Troubleshooting

### `GEMINI_API_KEY is missing or invalid`
- Ensure `.env` exists in project root.
- Ensure key name is exactly `GEMINI_API_KEY`.
- Restart terminal/app after setting env.

### “No test is ready”
- In Streamlit, generate questions first from Upload page.

### No questions returned from generator
- Source PDF may have little/empty extractable text.
- LLM output may fail schema checks (invalid options/answer/difficulty).
- Try clearer topic tag and richer source material.

### Correlations not displayed
- Not enough valid session data yet.

### Knowledge graph shows no roots
- No syllabus mapping stored yet, or selected topic has no ancestors.

---

## Known Limitations and Current Design Constraints

1. **Single-student UI mode**: Streamlit always uses `student_id = 1`.
2. **Fixed temporary upload filename**: uploaded PDF is saved as `temp_uploaded.pdf`.
3. **Question count can be less than requested**: invalid LLM outputs are dropped during normalization.
4. **Local-path assumptions**: DB and Chroma use relative paths (`student_helper.db`, `./chroma_db`).
5. **Limited test automation**: no formal unit/integration suite is currently included.
6. **Correlation minimum inconsistency**: report text says 3 sessions; backend computes with as few as 2 valid points.
7. **`phase4/agent.py` main block contains machine-specific custom PDF path** suitable for local testing only.

---

## Security and Privacy Notes

- Do not commit `.env` files or API keys.
- Uploaded PDFs are processed locally and text is sent to configured LLM endpoints for question generation/embedding.
- SQLite and Chroma data persist on local machine unless manually removed.

---

## Future Improvements (Recommended)

- Multi-student authentication and profile switching in Streamlit.
- Formal tests for parser, diagnostics, and DB flows.
- Better concurrency-safe temp file handling.
- Configurable model/provider settings through central config.
- CI pipeline with linting, tests, and type checking.
- Better observability (structured logs + per-module timing).

---

## License

This repository is currently intended for educational/project use. Add an explicit OSS license file (`LICENSE`) if you want standardized reuse terms.
