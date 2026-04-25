# AEGIS-MIND

AI-powered adaptive learning diagnostics for personalized student assessment.

AEGIS-MIND, also known as StudentHelper, is a Streamlit-based learning platform that turns uploaded study material into topic-focused MCQ tests, records student performance and session context, and generates diagnostic insights that explain where a learner is struggling and why.

The application combines retrieval-augmented question generation, SQLite-backed learning history, behavioral context tracking, statistical preprocessing, weakness scoring, syllabus-aware prerequisite mapping, and visual diagnostic dashboards into one local workflow.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [End-to-End Workflow](#end-to-end-workflow)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Repository Structure](#repository-structure)
- [Database Schema](#database-schema)
- [Analytics Engine](#analytics-engine)
- [RAG Question Generation](#rag-question-generation)
- [Streamlit Pages](#streamlit-pages)
- [Setup](#setup)
- [Configuration](#configuration)
- [Running the App](#running-the-app)
- [Useful Commands](#useful-commands)
- [Troubleshooting](#troubleshooting)
- [Security and Privacy](#security-and-privacy)
- [Current Scope](#current-scope)
- [Roadmap](#roadmap)
- [License](#license)

---

## Overview

AEGIS-MIND is designed around a simple idea: a student should not only know what they got wrong, but also understand the deeper learning pattern behind their mistakes.

The system helps answer questions such as:

- Which topic needs the most attention right now?
- Is a weak score caused by broad conceptual weakness or a specific mental block?
- Are sleep and stress correlated with recent performance?
- Which prerequisite topics should be reviewed before retrying a weak area?
- Can a test be generated directly from the student's own notes?

The current app runs as a local Streamlit experience and uses a single-student UI flow by default, while the underlying database schema supports multiple students.

---

## Key Features

- **PDF-based test generation**: Upload a notes PDF and generate MCQs from its extracted content.
- **RAG pipeline**: Extracts, chunks, embeds, retrieves, and uses relevant context for question generation.
- **Gemini integration**: Uses Gemini embeddings and Gemini chat generation through LangChain integrations.
- **Adaptive topic focus**: Recommends the highest-priority weak topic based on weighted performance.
- **Session logging**: Captures sleep, stress, response time, answer correctness, difficulty, and time of day.
- **Lucky-guess detection**: Flags suspiciously fast correct answers using IQR and hard-floor heuristics.
- **Weakness Index scoring**: Computes topic-level weakness from accuracy and concept weightage.
- **Kurtosis diagnosis**: Distinguishes general weakness from specific performance blocks when enough data exists.
- **Environmental correlation**: Calculates Pearson correlations between performance, sleep, and stress.
- **Syllabus mapping**: Parses syllabus text into ordered topics and builds prerequisite chains.
- **Knowledge graph support**: Uses syllabus-derived edges to suggest root-cause prerequisite topics.
- **Interactive dashboard**: Presents focus topics, weakness charts, report cards, and performance history.
- **Local persistence**: Stores structured learning history in SQLite and vector data in Chroma.

---

## End-to-End Workflow

1. Launch the Streamlit app.
2. Open the Upload and Generate page.
3. Enter pre-session vitals such as sleep hours and stress level.
4. Upload a PDF and provide a topic tag.
5. AEGIS-MIND extracts PDF text, chunks it, embeds it, retrieves relevant context, and generates MCQs.
6. Generated questions are saved to SQLite for the current test session.
7. The student takes the test inside the Streamlit interface.
8. The app logs answers, timing, difficulty, and correctness.
9. Preprocessing flags likely lucky guesses and imputes missing behavioral data where needed.
10. Diagnostics update the student's topic profile and report.
11. The dashboard and diagnostic report show current focus areas, weakness levels, correlations, and prerequisite recommendations.

---

## Architecture

```text
PDF notes
   |
   v
Text extraction -> Chunking -> Gemini embeddings -> Chroma vector store
   |                                                    |
   |                                                    v
   +-------------------------------------------> Relevant context
                                                        |
                                                        v
                                             Gemini MCQ generation
                                                        |
                                                        v
                                               SQLite question store
                                                        |
                                                        v
                                                Streamlit test flow
                                                        |
                                                        v
                                          Logs + preprocessing + analytics
                                                        |
                                                        v
                                    Dashboard, diagnostic report, recommendations
```

The project is organized into focused layers:

- `core/db`: schema creation and seed data.
- `core/generator`: PDF extraction, chunking, embedding, retrieval, and question generation.
- `core/runner`: session creation, question storage, test execution, and answer logging.
- `core/analytics`: preprocessing, weakness scoring, kurtosis, correlations, and knowledge graph logic.
- `core/syllabus`: syllabus parsing and prerequisite edge generation.
- `pages`: Streamlit multipage UI.
- `scripts`: helper scripts for manual inspection or subject-specific utilities.

---

## Technology Stack

| Area | Tools |
| --- | --- |
| App framework | Streamlit |
| Language | Python |
| Database | SQLite |
| Data processing | pandas, numpy |
| Statistics | scipy |
| Visualization | Plotly |
| PDF extraction | PyMuPDF |
| RAG framework | LangChain Core, LangChain Text Splitters, LangChain Chroma |
| Vector store | Chroma |
| AI provider | Google Gemini via `langchain-google-genai` |
| Graph analysis | NetworkX |
| Environment management | python-dotenv |

Pinned dependencies are listed in `requirements.txt`.

---

## Repository Structure

```text
StudentHelper/
|-- app.py
|-- README.md
|-- requirements.txt
|-- student_helper.db
|-- core/
|   |-- analytics/
|   |   |-- diagnostics.py
|   |   |-- environmental_correlation.py
|   |   |-- knowledge_graph.py
|   |   |-- kurtosis_analysis.py
|   |   |-- preprocessing.py
|   |   |-- weakness_index.py
|   |   `-- __init__.py
|   |-- db/
|   |   |-- database_init.py
|   |   |-- seed_data.py
|   |   `-- __init__.py
|   |-- generator/
|   |   |-- chunker.py
|   |   |-- embedder.py
|   |   |-- generate_test_pdf.py
|   |   |-- ocr_extractor.py
|   |   |-- pipeline.py
|   |   |-- question_generator.py
|   |   |-- rag_engine.py
|   |   |-- test_embed.py
|   |   `-- __init__.py
|   |-- runner/
|   |   |-- agent.py
|   |   |-- question_store.py
|   |   |-- session_logger.py
|   |   |-- test_runner.py
|   |   `-- __init__.py
|   |-- syllabus/
|   |   |-- syllabus_parser.py
|   |   `-- __init__.py
|   `-- __init__.py
|-- docs/
|   |-- Testing_Guide.md
|   |-- how to run main app.md
|   `-- hereyougo.md
|-- pages/
|   |-- 1_Dashboard.py
|   |-- 2_Upload_and_Generate.py
|   |-- 3_Take_Test.py
|   |-- 4_Diagnostic_Report.py
|   `-- 5_Syllabus_Mapping.py
`-- scripts/
    |-- displayall.py
    `-- electrostatics_summary.py
```

Generated local files such as `.env`, `chroma_db/`, uploaded PDFs, and database journal files should remain uncommitted.

---

## Database Schema

The application uses `student_helper.db`, created automatically through `core/db/database_init.py`.

### `Students`

Stores student identity.

| Column | Purpose |
| --- | --- |
| `Student_ID` | Primary key |
| `Student_Name` | Display name |

### `Student_Profile`

Stores per-student, per-topic learning profile state.

| Column | Purpose |
| --- | --- |
| `Student_ID` | Student reference |
| `Topic_Tag` | Topic identifier |
| `Weakness_Index` | Weighted weakness score |
| `Concept_Weightage` | Topic importance multiplier |
| `Last_Tested_Date` | Most recent test date |
| `Session_Cluster_State` | Reserved profile state |
| `Total_Sessions` | Number of sessions for this topic |
| `Average_Accuracy` | Current average accuracy |
| `Cumulative_Time_Spent` | Reserved cumulative timing field |

### `Behavioural_Log`

Stores test-level context and session metadata.

| Column | Purpose |
| --- | --- |
| `Session_ID` | Primary key |
| `Student_ID` | Student reference |
| `Test_ID` | Unique test identifier |
| `Sleep_Hours` | Sleep before session |
| `Stress_Level` | Self-reported stress from 1 to 10 |
| `Session_Date` | Session date |
| `Session_Duration_Seconds` | Total answer time |
| `Is_Imputed` | Whether sleep was imputed |

### `Questions`

Stores generated MCQs for a test.

| Column | Purpose |
| --- | --- |
| `Question_ID` | Primary key |
| `Student_ID` | Student reference |
| `Test_ID` | Test reference |
| `Topic_Tag` | Topic identifier |
| `Question_Text` | Generated question |
| `Options` | JSON-encoded answer options |
| `Correct_Answer` | Correct option letter |
| `Difficulty_Level` | Difficulty from 1 to 3 |
| `Was_Asked` | Whether the question has been attempted |

### `Academic_Performance_Log`

Stores answer-level performance data.

| Column | Purpose |
| --- | --- |
| `Log_ID` | Primary key |
| `Student_ID` | Student reference |
| `Test_ID` | Test reference |
| `Topic_Tag` | Topic identifier |
| `Question_ID` | Question reference |
| `Outcome` | `1` for correct, `0` for incorrect |
| `Time_Spent_Seconds` | Time spent on question |
| `Difficulty_Level` | Difficulty from 1 to 3 |
| `Time_of_Day` | Attempt time |
| `Test_Sequence_Number` | Question order in test |
| `Is_Lucky_Guess` | Preprocessing flag |

### `Syllabus_Topics`

Stores parsed syllabus topics and ordering.

| Column | Purpose |
| --- | --- |
| `Subject_Name` | Subject identifier |
| `Unit_Number` | Unit number |
| `Topic_Name` | Parsed topic name |
| `Topic_Order` | Topic position within the unit |

---

## Analytics Engine

### Preprocessing

Implemented in `core/analytics/preprocessing.py`.

The preprocessing pipeline:

- Loads academic and behavioral logs from SQLite.
- Flags likely lucky guesses when correct answers are completed unusually fast.
- Uses an IQR-based detector per difficulty level when enough samples exist.
- Applies a hard-floor rule for correct answers faster than two seconds.
- Computes normalized and standardized timing metrics in memory.
- Imputes missing sleep data using historical mean sleep or a default fallback.
- Saves lucky-guess and imputation flags back to SQLite.

### Weakness Index

Implemented in `core/analytics/weakness_index.py`.

```text
Weakness_Index = (1 - Accuracy) * Concept_Weightage
```

Accuracy is computed per student and topic while excluding rows flagged as lucky guesses.

### Kurtosis Diagnosis

Implemented in `core/analytics/kurtosis_analysis.py`.

The module adjusts time spent by difficulty-level mean and computes excess kurtosis per topic.

| Result | Meaning |
| --- | --- |
| `Specific Block` | Heavy-tailed timing pattern, suggesting isolated blockers or outlier struggles |
| `General Weakness` | Broader weakness pattern across the topic |
| `Insufficient Data` | Fewer than four observations for a reliable kurtosis estimate |

### Environmental Correlation

Implemented in `core/analytics/environmental_correlation.py` and exposed per student in `core/analytics/diagnostics.py`.

The app computes Pearson correlations between:

- Sleep hours and session accuracy.
- Stress level and session accuracy.

### Knowledge Graph

Implemented in `core/analytics/knowledge_graph.py`.

The knowledge graph is built from syllabus topic order. Consecutive topics within the same unit become directed prerequisite edges, and weak-topic root causes are discovered using graph ancestors.

---

## RAG Question Generation

The generation flow lives in `core/generator`.

1. `ocr_extractor.py` opens the uploaded PDF with PyMuPDF and extracts page text.
2. `chunker.py` splits text into overlapping LangChain documents with page and topic metadata.
3. `embedder.py` embeds chunks with `models/gemini-embedding-001` and stores them in Chroma.
4. `rag_engine.py` retrieves the top relevant chunks for the selected topic.
5. `question_generator.py` uses `gemini-2.5-flash-lite` to generate structured MCQs.
6. `pipeline.py` orchestrates the full flow and returns normalized question objects.

The question generator expects JSON output and includes normalization logic for common model-output variations, including answer formats, key aliases, and difficulty values.

---

## Streamlit Pages

### Home

File: `app.py`

- Sets Streamlit page configuration.
- Initializes the database safely.
- Uses `student_id = 1` for the current single-student UI mode.

### Dashboard

File: `pages/1_Dashboard.py`

- Shows the recommended focus topic.
- Displays weakness by topic.
- Presents detailed topic metrics.
- Shows aggregate session statistics.

### Upload and Generate

File: `pages/2_Upload_and_Generate.py`

- Captures sleep and stress inputs.
- Accepts PDF upload.
- Accepts topic tag.
- Creates a session.
- Runs the RAG pipeline.
- Stores generated questions for the test.

### Take Test

File: `pages/3_Take_Test.py`

- Loads generated questions.
- Tracks answer selection and response time.
- Marks questions as asked.
- Logs results.
- Runs preprocessing and diagnostics after completion.
- Shows score and answer breakdown.

### Diagnostic Report

File: `pages/4_Diagnostic_Report.py`

- Ranks topics by Weakness Index.
- Shows kurtosis-based interpretation.
- Displays sleep and stress correlations when enough data exists.
- Lists knowledge-graph prerequisite recommendations.
- Plots performance history.

### Syllabus Mapping

File: `pages/5_Syllabus_Mapping.py`

- Accepts subject name and unit-wise syllabus text.
- Parses topic sequences.
- Stores syllabus topics in SQLite.
- Shows derived prerequisite edges.
- Displays currently stored syllabi.

---

## Setup

### Prerequisites

- Python 3.10 or newer recommended.
- A Google Gemini API key.
- Internet access for embedding and question-generation calls.

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd StudentHelper
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Windows Command Prompt:

```cmd
.venv\Scripts\activate.bat
```

macOS or Linux:

```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Configuration

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

The app reads this key inside the embedding and question-generation modules.

Do not commit `.env` to version control.

---

## Running the App

Start the Streamlit interface:

```bash
streamlit run app.py
```

Then use the sidebar navigation:

1. Open **Syllabus Mapping** if you want prerequisite-aware diagnostics.
2. Open **Upload and Generate** to create a test from a PDF.
3. Open **Take Test** to answer the generated MCQs.
4. Open **Dashboard** or **Diagnostic Report** to review results.

The database is initialized automatically when the app starts.

---

## Useful Commands

Initialize the database manually:

```bash
python -m core.db.database_init
```

Seed demo data:

```bash
python -m core.db.seed_data
```

Run preprocessing manually:

```bash
python -m core.analytics.preprocessing
```

Run diagnostics manually:

```bash
python -m core.analytics.diagnostics
```

Run the RAG pipeline directly:

```bash
python -m core.generator.pipeline path/to/notes.pdf "Topic Tag"
```

Run the terminal-based agent workflow:

```bash
python -m core.runner.agent
```

Run syllabus parser smoke tests:

```bash
python -m core.syllabus.syllabus_parser
```

Reset local generated data on Windows PowerShell:

```powershell
Remove-Item -Path "student_helper.db" -Force -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "chroma_db\" -ErrorAction SilentlyContinue
```

After resetting, start the app again or run:

```bash
python -m core.db.seed_data
```

---

## Troubleshooting

### `GEMINI_API_KEY is missing or invalid in the .env file`

Check that:

- `.env` exists in the project root.
- The variable name is exactly `GEMINI_API_KEY`.
- The value is not empty or left as a placeholder.
- The terminal or Streamlit process has been restarted after editing `.env`.

### No test is ready

Generate questions first from the Upload and Generate page. The Take Test page depends on `questions_ready`, `current_test_id`, and `current_topic` in Streamlit session state.

### No questions are generated

Possible causes:

- The PDF has little or no extractable text.
- The topic tag does not match the uploaded material well.
- The model returned malformed output that failed validation.
- The Gemini API call failed or was rate-limited.

Try a clearer topic tag, a text-rich PDF, or a smaller source document.

### Diagnostic report has limited data

Some diagnostics need minimum sample sizes:

- Kurtosis needs at least four timing observations per topic.
- Correlation needs at least two valid sessions in the backend.
- Knowledge-graph roots require saved syllabus mapping data.

### Dashboard shows no profile data

Run seed data or create a student profile entry before testing:

```bash
python -m core.db.seed_data
```

### Chroma or generated content feels stale

Reset the vector store:

```powershell
Remove-Item -Recurse -Force "chroma_db\" -ErrorAction SilentlyContinue
```

---

## Security and Privacy

- Uploaded PDFs are processed locally for extraction, but their text is sent to Gemini for embeddings and question generation.
- API keys must be stored in `.env` and excluded from version control.
- SQLite and Chroma data are stored locally.
- Generated questions, answers, timing data, sleep, and stress values are persisted in `student_helper.db`.
- Avoid committing real student data, uploaded PDFs, local databases, or vector stores.

---

## Current Scope

AEGIS-MIND is ready to run as a local adaptive-learning application with a polished Streamlit flow and an integrated analytics pipeline.

Current implementation details to be aware of:

- The Streamlit UI uses a single-student mode with `student_id = 1`.
- The schema supports multiple students, and seed data includes two demo students.
- Uploaded PDFs are temporarily saved as `temp_uploaded.pdf`.
- Generated question count may be lower than requested if model output fails validation.
- There is no formal automated test suite yet.
- The terminal agent includes a custom local PDF path in its `__main__` block for manual experimentation.
- Correlation display text expects richer session history, so early sessions may show limited insights.

---

## Roadmap

Potential next improvements:

- Multi-student login and profile switching.
- Automated tests for parser, database flows, analytics, and question normalization.
- Configurable model/provider settings.
- Safer unique upload filenames for concurrent sessions.
- Admin page for managing students, topics, and syllabus data.
- Exportable diagnostic reports.
- CI checks for formatting, linting, and regression tests.
- Better observability with structured logs and module-level timings.

---

## License

This repository is currently intended for educational and project use. Add a dedicated `LICENSE` file before distributing it as open-source software.
