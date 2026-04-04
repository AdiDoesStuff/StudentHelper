# StudentHelper Project

## Overview

The **StudentHelper** project provides a diagnostic suite for analyzing student performance, identifying weaknesses, and correlating lifestyle factors with academic outcomes. This repository contains scripts for database initialization, data seeding, preprocessing, and comprehensive diagnostics.

---

## 📋 Execution Order

To reproduce the full workflow and generate the final diagnostic reports, run the scripts in the following order:

1. **Initialize the database schema**
   ```bash
   python database_init.py
   ```
   Creates the `student_helper.db` SQLite database with all required tables.

2. **Seed the database with sample data**
   ```bash
   python seed_data.py
   ```
   Populates the database with two example students, behavioural logs, and academic performance logs.

3. **Run the preprocessing pipeline**
   ```bash
   python preprocessing.py
   ```
   - Detects lucky‑guess answers using IQR analysis.
   - Normalizes and standardizes time‑spent metrics.
   - Imputes missing behavioural data (e.g., sleep hours) and flags imputed rows.
   - Writes the processed flags back to the database.

4. **Execute the full diagnostic suite**
   ```bash
   python diagnostics.py
   ```
   - Computes weakness indices for every student.
   - Performs kurtosis‑based diagnosis.
   - Builds a knowledge‑graph of topic prerequisites.
   - Calculates per‑student lifestyle correlations (sleep & stress).
   - Generates a detailed report for each student, including:
     - Primary focus area (weakest topic)
     - Weakness index & accuracy
     - Diagnosis label
     - Lifestyle correlation summary
     - Root prerequisite topics to review

---

## 🛠️ Individual Modules (Optional)

If you wish to run specific components independently, you can import the following modules:

- `weakness_index.py` – `compute_weakness()`
- `kurtosis_analysis.py` – `analyze_kurtosis()`
- `environmental_correlation.py` – `analyze_environmental_correlation()`
- `knowledge_graph.py` – `build_knowledge_graph()` & `get_root_causes()`

These functions are called internally by `diagnostics.py`, but can be used for custom analyses.

---

## 📦 Dependencies

```bash
pip install -r requirements.txt
```
*(If a `requirements.txt` file is not present, install the following packages manually: `pandas`, `numpy`, `scipy`, `networkx`.)*

---

## 🚀 Quick Start

```bash
# 1. Create/refresh the database schema
python database_init.py

# 2. Populate with seed data
python seed_data.py

# 3. Preprocess the raw logs
python preprocessing.py

# 4. Run the full diagnostics and view the console output
python diagnostics.py
```

---

## 📄 License

This project is provided for educational purposes. Feel free to adapt and extend the code.
