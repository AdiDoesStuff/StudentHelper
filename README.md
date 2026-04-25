# AEGIS-MIND

**AI-Powered Adaptive Learning & Performance Diagnostics**

AEGIS-MIND (StudentHelper) is an intelligent, local-first learning platform designed to uncover the *why* behind student performance. By transforming raw study materials into topic-aware assessments, it maps learning gaps through statistical diagnostics and behavioral context tracking.

---

## 🚀 The AEGIS-MIND Workflow

1.  **Map:** Define your subject hierarchy and unit-wise topics.
2.  **Ingest:** Upload multiple PDFs; local AI automatically sorts content into the defined topics.
3.  **Study:** Review re-assembled, topic-specific material via the Study Material Viewer.
4.  **Assess:** Take MCQ tests generated via Retrieval-Augmented Generation (RAG).
5.  **Diagnose:** Analyze performance through a dashboard that tracks weakness indices, behavioral correlations, and prerequisite root causes.

---

## ✨ Key Features

### 🧠 Intelligent Ingestion (Local-First)
- **Automatic Multi-File Sorting:** Uses the `all-MiniLM-L6-v2` model to classify document chunks into syllabus topics locally (Zero API cost).
- **RAG-Powered Retrieval:** High-performance local vector search for context-aware assessment generation.

### 📊 Advanced Diagnostics
- **Weakness Indexing:** Weighted scoring that accounts for topic importance and historical accuracy.
- **Kurtosis Diagnosis:** Statistically distinguishes between general conceptual weakness and isolated "mental blocks."
- **Behavioral Correlation:** Identifies how sleep and stress levels impact accuracy using Pearson correlation.
- **Root-Cause Analysis:** Leverages a prerequisite knowledge graph to suggest which foundational topics to review.

### 🛠️ User-Centric Design
- **Contextual Awareness:** Tracks response timing and flags "lucky guesses" using IQR-based anomaly detection.
- **Unified Study Hub:** Centralized access to study materials, performance history, and adaptive recommendations.

---

## 💻 Tech Stack

| Component | Technology |
| :--- | :--- |
| **Frontend** | Streamlit |
| **Data Engine** | Pandas, NumPy, Scikit-Learn |
| **Analytics** | SciPy, NetworkX |
| **Storage** | SQLite (Relational), ChromaDB (Vector) |
| **AI (Local)** | Sentence-Transformers (all-MiniLM-L6-v2) |
| **AI (Cloud)** | Google Gemini (MCQ Generation) |

---

## 🛠️ Setup & Execution

### 1. Installation
```bash
# Clone and enter directory
git clone <repo-url>
cd StudentHelper

# Setup environment
python -m venv .venv
source .venv/bin/activate  # Or .\.venv\Scripts\Activate.ps1 for Windows
pip install -r requirements.txt
```

### 2. Configuration
Create a `.env` file in the root:
```env
GEMINI_API_KEY=your_key_here
```

### 3. Launch
```bash
streamlit run app.py
```

---

## 📂 Project Architecture

- **`core/analytics`**: Statistical engines (kurtosis, correlation, weakness index).
- **`core/generator`**: Local AI classifier, RAG retrieval, and MCQ generation.
- **`core/runner`**: Test execution and high-fidelity session logging.
- **`core/syllabus`**: Prerequisite mapping and hierarchy parsing.
- **`pages/`**: The multi-stage diagnostic dashboard and study interface.

---

## 🛡️ Privacy & Performance
AEGIS-MIND prioritizes privacy and efficiency. All document processing, topic classification, and embedding storage occur **locally**. Cloud AI is utilized strictly for high-reasoning tasks like question generation, ensuring minimal token usage and maximum data control.
