<div align="center">

# 🧠 AEGIS-MIND

### AI-Powered Adaptive Learning & Performance Diagnostics

AEGIS-MIND is a local-first learning analytics platform that converts study material, syllabus maps, generated assessments, and imported Evalify results into a single diagnostic profile for one student.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Local_DB-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Search-5B5BD6?style=for-the-badge)
![Gemini](https://img.shields.io/badge/Gemini-Question_Generation-4285F4?style=for-the-badge&logo=google&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-Llama_3.3_70B-F55036?style=for-the-badge)

</div>

---

## ✨ Overview

**AEGIS-MIND**, also known as **StudentHelper**, is designed to answer a deeper question than “what score did I get?” It helps identify **why** performance changes across topics by combining:

- 📚 syllabus-aware study material ingestion
- 🎯 AI-generated MCQ assessments
- 📊 weakness indexing and statistical diagnostics
- 🧩 prerequisite/root-cause analysis
- 💤 sleep and stress context tracking
- 📥 external Evalify result imports

The application runs as a Streamlit dashboard, stores data locally in SQLite and ChromaDB, and uses cloud LLMs only when generating questions.

---

## 🚀 Product Workflow

| Stage | What Happens |
| :--- | :--- |
| 🗺️ **Map** | Create a structured syllabus by subject, unit, and topic. |
| 📄 **Ingest** | Upload PDFs and classify extracted chunks into syllabus topics. |
| 📖 **Study** | Review topic-specific material generated from uploaded content. |
| 🎯 **Assess** | Generate MCQ tests using Gemini or Groq over local RAG context. |
| 📥 **Import** | Bring completed Evalify quiz results into the same diagnostic system. |
| 🧪 **Process** | Run preprocessing for behavioral imputation and lucky-guess handling. |
| 📊 **Diagnose** | Review weak topics, behavioral correlations, and prerequisite gaps. |

---

## 🧩 Core Capabilities

### 📚 Local-First Study Intelligence

- Multi-PDF ingestion with topic-aware chunking.
- Local semantic classification using `sentence-transformers`.
- `all-MiniLM-L6-v2` embeddings for fast topic matching.
- ChromaDB-backed vector search for retrieval-augmented generation.
- Topic-specific study material viewer.

### 🤖 AI Test Generation

- Multi-topic MCQ generation from selected syllabus topics.
- RAG retrieval from locally processed study material.
- Provider selection between:
  - **Google Gemini** via `GEMINI_API_KEY`
  - **Groq Llama 3.3 70B** via `GROQ_API_KEY`
- Structured JSON validation and normalization for generated questions.
- In-app test-taking with session logging.

### 📥 Evalify Import Integration

- Browser-based Tampermonkey exporter for Evalify result pages.
- One-click `Copy JSON for AEGIS-MIND` button on supported Evalify quiz results.
- Streamlit import page for validating, previewing, tagging, and importing results.
- MCQ-only filtering for compatibility with diagnostics.
- Duplicate import detection through `External_Test_ID`.
- Local embedding-based topic tagging against your syllabus.
- Optional diagnostics run immediately after import.

> Full setup guide: [EvalifyImport.md](EvalifyImport.md)

### 📊 Diagnostics & Analytics

- Topic-level **Weakness Index** calculation.
- IQR-based lucky-guess detection for timed in-app tests.
- Safe handling for Evalify imports with missing timing data.
- Sleep-hour imputation with `Is_Imputed` tracking.
- Sleep/stress correlation analysis.
- Kurtosis-based detection of broad weakness vs isolated mental blocks.
- Knowledge graph based root-cause analysis.
- Dashboard recommendation for the highest-priority focus topic.

---

## 🛠️ Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Frontend** | Streamlit |
| **Data Processing** | Pandas, NumPy, SciPy, Scikit-Learn |
| **Visualization** | Plotly |
| **Local Embeddings** | Sentence Transformers |
| **Vector Store** | ChromaDB via LangChain Chroma |
| **LLM Providers** | Google Gemini, Groq Llama 3.3 70B |
| **PDF Extraction** | PyMuPDF |
| **Database** | SQLite |
| **Browser Automation** | Tampermonkey userscript |

---

## 📁 Project Structure

```text
StudentHelper/
├── app.py                         # Streamlit entry point
├── README.md                      # Product overview
├── EvalifyImport.md               # Evalify import guide
├── tampermonkey_script.js         # Evalify result-page exporter
├── requirements.txt               # Python dependencies
├── student_helper.db              # Local SQLite database
├── chroma_db/                     # Local vector database
├── core/
│   ├── analytics/                 # Diagnostics, preprocessing, weakness analysis
│   ├── db/                        # SQLite schema and migrations
│   ├── generator/                 # PDF extraction, embeddings, RAG, question generation
│   ├── runner/                    # Sessions, logging, Evalify imports
│   └── syllabus/                  # Syllabus parsing helpers
└── pages/
    ├── 1_Dashboard.py
    ├── 2_Upload_and_Generate.py
    ├── 3_Study_Material.py
    ├── 4_Generate_Test.py
    ├── 5_Take_Test.py
    ├── 6_Diagnostic_Report.py
    ├── 7_Syllabus_Mapping.py
    └── 8_Import_Evalify.py
```

---

## ⚙️ Installation

> **Use the virtual environment for every Python command.**  
> This keeps AEGIS-MIND dependencies isolated from your global Python install and avoids version conflicts.

### 1. Create a virtual environment

```bash
python -m venv .venv
```

### 2. Activate the environment

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

> The first run may download local embedding model weights for `sentence-transformers`.

### 4. Configure API keys

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_key_here
GROQ_API_KEY=your_groq_key_here
```

### 5. Launch the app

```bash
python -m streamlit run app.py
```

Using `python -m streamlit` ensures Streamlit is launched from the active `.venv`, not from a global Python installation. The database is initialized automatically. The Evalify import page also runs safe migrations for import metadata columns.

### Windows shortcut

On Windows, you can also run:

```powershell
.\run_app.bat
```

The batch file checks for `.venv\Scripts\python.exe`, injects `.venv\Scripts` into `PATH`, and launches Streamlit through the virtual environment.

---

## 🧭 Using AEGIS-MIND

1. Open **Syllabus Mapping** and define your subject, units, and topics.
2. Open **Upload and Generate** to upload PDFs and prepare study material.
3. Open **Study Material** to review extracted topic-wise content.
4. Open **Generate Test** to create MCQs from selected topics.
5. Complete the assessment in **Take Test**.
6. Open **Import Evalify** to add external Evalify quiz performance.
7. Review **Dashboard** and **Diagnostic Report** for recommendations.

---

## 🔐 Privacy & Data Control

| Data Type | Location |
| :--- | :--- |
| Uploaded PDFs | Local workspace |
| SQLite performance logs | `student_helper.db` |
| Vector embeddings | `chroma_db/` |
| Evalify imports | Local database after manual paste |
| LLM generation context | Sent only when generating questions |

AEGIS-MIND is local-first by design. Study material processing, embeddings, classification, storage, and diagnostics happen locally. Gemini and Groq are used only for question generation from retrieved context.

---

## 📌 Important Notes

- The current application is designed for a single default student: `Student_ID = 1`.
- Evalify imports currently support MCQ questions only.
- Descriptive and coding questions exported from Evalify are intentionally skipped during import.
- In-app tests include timing data; Evalify imports do not, so lucky-guess detection handles them separately.

---

## 🧾 Key Files

| File | Purpose |
| :--- | :--- |
| `core/generator/question_generator.py` | Gemini/Groq MCQ generation and JSON validation |
| `core/generator/test_builder.py` | Multi-topic RAG test assembly |
| `core/runner/evalify_importer.py` | Evalify filtering, topic tagging, and DB import |
| `core/analytics/preprocessing.py` | Lucky-guess detection and behavioral imputation |
| `core/db/database_init.py` | Schema creation and safe migrations |
| `tampermonkey_script.js` | Evalify browser exporter |

---

<div align="center">

**AEGIS-MIND turns study history into an actionable learning map.**

</div>
