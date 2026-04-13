# AEGIS-MIND (StudentHelper Project)

## 🌟 Overview
**AEGIS-MIND** (formerly StudentHelper) is an advanced, AI-powered adaptive learning and diagnostic suite. It deeply analyzes student performance, identifies core weaknesses, correlates lifestyle factors with academic outcomes, and dynamically generates custom educational content using a Retrieval-Augmented Generation (RAG) pipeline.

---

## ✨ Key Features

### 1. 🧠 Core Diagnostic Engine
- **Weakness Indexing:** Statistically identifies the weakest topics for targeted improvement.
- **Kurtosis Analysis:** Analyzes the distribution of response times to differentiate fundamental mental blocks from simple knowledge deficits.
- **Environmental Correlation:** Maps external life factors (like sleep and stress) to academic performance.
- **Knowledge Graphing:** Maps prerequisite topics to track down the root causes of academic weaknesses.

### 2. 📚 RAG Pipeline (Phase 3)
- **PDF Ingestion:** Upload custom textbooks and study materials.
- **Intelligent Processing:** Automatically extracts, chunks, and embeds text into a local ChromaDB vector database.
- **Dynamic Question Generation:** Uses LLMs to craft hyper-targeted Multiple Choice Questions (MCQs) grounded securely in the provided study material.

### 3. 🤖 Tutor Agent Logic (Phase 4)
- **Session Orchestration:** Coordinates the tutor agent flow, evaluating target weaknesses before starting.
- **Vitals Collection:** Gathers pre-session behavioural readings for contextual analysis.
- **Dynamic Testing:** Serves the generated questions to the student and meticulously logs interactions and correctness.

### 4. 🖥️ Interactive Web UI
- Built using **Streamlit** for a seamless, browser-based user experience.
- **Dashboard:** At-a-glance overview of student data and system state.
- **Upload & Generate:** Interface for the RAG pipeline to ingest PDFs and create test questions.
- **Take Test:** An interactive, session-managed testing environment.
- **Diagnostic Report:** Visualized readouts of all diagnostic metrics.

---

## 🏗️ Project Architecture

```plaintext
StudentHelper/
├── app.py                      # Main Streamlit UI Entry Point
├── pages/                      # Streamlit application views
│   ├── 1_Dashboard.py          # Visual overview
│   ├── 2_Upload_and_Generate.py# RAG interface
│   ├── 3_Take_Test.py          # Interactive testing environment
│   └── 4_Diagnostic_Report.py  # Results & visualizations
├── phase3/                     # Retrieval-Augmented Generation (RAG) Pipeline
│   ├── ocr_extractor.py        # PDF text extraction
│   ├── chunker.py              # Text tokenization & chunking
│   ├── embedder.py             # Vector embedding integration
│   ├── rag_engine.py           # ChromaDB semantic search
│   ├── question_generator.py   # LLM MCQ prompt engineering
│   └── pipeline.py             # Master pipeline orchestrator
├── phase4/                     # Agentic Session Logic
│   ├── agent.py                # Core decision engine & session control
│   ├── test_runner.py          # Quiz execution flow
│   ├── session_logger.py       # Metadata & logging
│   └── question_store.py       # Active session question caching
├── database_init.py            # SQLite schema initialization
├── seed_data.py                # Baseline mockup data populizer
├── preprocessing.py            # Data cleaning & standardization
└── diagnostics.py              # Parent diagnostic orchestration
```

---

## 📋 Execution Order (Terminal Workflow)

If you prefer to operate directly from the terminal bypassing the UI, you can execute the lifecycle manually:

1. **Initialize the database schema**
   ```bash
   python database_init.py
   ```
2. **Seed the database with sample data**
   ```bash
   python seed_data.py
   ```
3. **Run the preprocessing pipeline**
   ```bash
   python preprocessing.py
   ```
4. **Execute the full diagnostic suite**
   ```bash
   python diagnostics.py
   ```
5. **Run the RAG Generation Pipeline** (from `phase3` directory)
   ```bash
   python phase3/pipeline.py
   ```

---

## 🚀 Quick Start (Web Interface)

To launch the fully featured **AEGIS-MIND** end-to-end interface:

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   *(If not present, install manually: `streamlit`, `pandas`, `numpy`, `scipy`, `networkx`, `sqlite3`, any necessary RAG libraries `chromadb`, etc.)*

2. **Set Environment Keys:**
   Create a `.env` file in the root directory and ensure API keys (e.g. Gemini) are defined.

3. **Boot the Interface:**
   ```bash
   streamlit run app.py
   ```
   *This automatically initializes the database schema if missing.*

---

## 📄 License
This project is provided for educational purposes. Feel free to adapt and extend the code.
