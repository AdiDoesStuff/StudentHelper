# Project File Analysis Report

This document provides a comprehensive structural breakdown of the `StudentHelper` (AEGIS-MIND) project. I have analyzed the directory structure and each file's role using its Abstract Syntax Tree (classes, functions, etc.) to keep it token-efficient and highly accurate.

## 📁 Root Directory (Database & Diagnostic Pipeline)
The root folder serves as the core diagnostic engine, handling database initialization, data preprocessing, and generating statistical insights about students.

* **`app.py`**
  * **Role:** The main entry point for the Streamlit-based web application. It configures the user interface and initializes the application state.
* **`database_init.py`** 
  * **Role:** Initializes the application's underlying SQLite database.
  * **Key Components:** Contains the `init_db` function to orchestrate table creation and relationships.
* **`seed_data.py`** 
  * **Role:** Stuffs the SQLite database with generated mock data or baseline student entries.
  * **Key Components:** `seed_data` function.
* **`preprocessing.py`** 
  * **Role:** Handles the data cleaning pipeline prior to analysis.
  * **Key Components:** Uses object-oriented design via the `PreprocessingPipeline` class. Runs scaling (`scale_metrics`), imputes missing data (`impute_behavioural`), and identifies outliers (`detect_lucky_guesses`).
* **`diagnostics.py`** 
  * **Role:** The master driver for the diagnostic phase. 
  * **Key Components:** Wraps various downstream tools and houses main flow functions like `run_diagnostics` and `get_student_correlation`.
* **`weakness_index.py`** 
  * **Role:** Computes weakness scores specific to topics for targeted improvements.
  * **Key Components:** `compute_weakness` function.
* **`kurtosis_analysis.py`** 
  * **Role:** Likely evaluates the statistical distribution of response times to sort fundamental blocks from simple knowledge deficits.
  * **Key Components:** `analyze_kurtosis` function.
* **`environmental_correlation.py`** 
  * **Role:** Studies correlations between a student's academic performance and external life factors (like sleep or stress).
  * **Key Components:** `analyze_environmental_correlation` function.
* **`knowledge_graph.py`** 
  * **Role:** Maps topics into a conceptual prerequisite graph to track down root causes of weaknesses.
  * **Key Components:** `build_knowledge_graph` and `get_root_causes` functions.
* **`displayall.py`** 
  * **Role:** Prints or manages raw database rows/tables for debugging. Provides quick view via `display_all`.
* **`electrostatics_summary.py`** 
  * **Role:** specialized script dedicated to summarizing test or topic metrics around electrostatics (`electrostatics_summary`).

## 📁 Streamlit UI (`pages/`)
The frontend dashboard environment allowing students to interact with tests and visualize their diagnostics interactively.

* **`1_Dashboard.py`**
  * **Role:** The primary landing page that displays overall weakness metrics, topic accuracy, and active session statistics using `plotly` charts.
* **`2_Upload_and_Generate.py`**
  * **Role:** Interface for collecting pre-session behavioral vitals (sleep, stress), uploading PDF documents, and orchestrating Phase 3 (RAG text extraction and Gemini question generation).
* **`3_Take_Test.py`**
  * **Role:** Facilitates active testing. Fetches dynamically generated questions from the DB, records timestamped answers, assesses them against the expected baseline, and updates session logs.
* **`4_Diagnostic_Report.py`**
  * **Role:** Comprehensive visual report containing advanced insights like Kurtosis logic, Environmental Correlation parameters, and Knowledge Graph topic hierarchies mapping out root causes.

## 📁 phase3/ (The RAG Pipeline)
The phase3 directory acts as the Retrieval-Augmented Generation environment. It ingests custom PDF textbooks to formulate targeted Multiple Choice Questions (MCQs).

* **`__init__.py`**
  * **Role:** Denotes the `phase3` directory as a python package.
* **`ocr_extractor.py`**
  * **Role:** The entry point for PDF ingestion; converts documents into raw text (`extract_text`).
* **`chunker.py`** 
  * **Role:** Slices the extracted text into manageable token chunks to prep for embedding (`chunk_text`).
* **`embedder.py`** 
  * **Role:** Connects to embedding models and populates the ChromaDB vector database (`embed_and_store`).
* **`rag_engine.py`** 
  * **Role:** Submits semantic search queries into the vector space to fetch localized textbook context (`retrieve_chunks`).
* **`question_generator.py`** 
  * **Role:** Uses Language Models grounded in retrieved chunks to dynamically craft accurate MCQs (`generate_questions`).
* **`pipeline.py`** 
  * **Role:** The primary orchestrator script for Phase 3 combining extraction, embedding, retrieval, and generation (`run_pipeline`).
* **Auxiliaries (`generate_test_pdf.py`, `test_embed.py`)** 
  * **Role:** Helper utilities for bootstrapping local testing pdfs and verifying the embedding layers functionality.
* **Sample PDFs (`test_electrostatics.pdf`, `test_linear_algebra.pdf`)**
  * **Role:** Baseline mock educational documents for testing RAG extraction capabilities.

## 📁 phase4/ (Agent Logic & Test Flow)
This folder manages test sessions (AEGIS-MIND logic). It's responsible for interacting with the student, monitoring their performance, and serving the diagnostic tests.

* **`__init__.py`**
  * **Role:** Denotes the `phase4` directory as a python package.
* **`agent.py`** 
  * **Role:** The core decision engine coordinating the tutor agent flow. 
  * **Key Components:** Evaluates target weaknesses (`get_weakest_topic`), takes behavioral readings (`collect_pre_session_vitals`), and wraps everything in `run_agent_session`.
* **`test_runner.py`** 
  * **Role:** Connects generated/persisted questions into an actionable quiz context evaluating student correctness (`run_test`).
* **`session_logger.py`** 
  * **Role:** Captures metadata on interaction durations and test results bridging logic back to the database backend. (`create_session`, `log_answers`).
* **`question_store.py`** 
  * **Role:** Responsible for saving and managing questions prepared for current test sessions (`store_questions`).

## 📁 Miscellanea / Context Directories
* **`.gitignore` & `.env`**: Version control masks and environment boundaries (secrets/keys like Gemini).
* **`requirements.txt`**: Records the comprehensive list of python dependencies required for running AEGIS-MIND.
* **`student_helper.db` & `chroma_db/`**: Your permanent relational SQLite structure and the local Vector store directory holding document embeddings.
* **`README.md` & `Tutorial .md's/Testing_Guide.md`**: Guidebooks for installing, analyzing capabilities, and executing module tests in chronological order.
