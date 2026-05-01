<div align="center">

# 📥 Evalify Import Guide

### Bring Evalify quiz results into AEGIS-MIND diagnostics

Use the included Tampermonkey exporter to copy completed Evalify quiz results as JSON, then import them into AEGIS-MIND for topic tagging, performance logging, and diagnostic analysis.

![Tampermonkey](https://img.shields.io/badge/Tampermonkey-Exporter-00485B?style=for-the-badge)
![Evalify](https://img.shields.io/badge/Evalify-Result_Import-6366F1?style=for-the-badge)
![AEGIS-MIND](https://img.shields.io/badge/AEGIS--MIND-Diagnostics-111827?style=for-the-badge)

</div>

---

## 🎯 What This Integration Does

The Evalify import workflow lets you convert a completed Evalify quiz result page into records that AEGIS-MIND can analyze.

| Component | Role |
| :--- | :--- |
| `tampermonkey_script.js` | Adds a copy/export button to Evalify result pages. |
| Evalify result page | Source page containing completed quiz answers and marks. |
| Clipboard JSON | Transfer format between Evalify and AEGIS-MIND. |
| `pages/8_Import_Evalify.py` | Streamlit import UI for validation, preview, tagging, and import. |
| `core/runner/evalify_importer.py` | Filters MCQs, classifies topics, checks duplicates, and writes to SQLite. |

> ✅ MCQ questions are imported into diagnostics.  
> ⚠️ Coding and descriptive questions may be exported, but are skipped during import because the current analytics pipeline expects MCQ-style outcomes.

---

## ✅ Requirements

Before starting, make sure you have:

- 🌐 A browser supported by Tampermonkey, such as Chrome, Edge, Brave, or Firefox.
- 🧩 The Tampermonkey browser extension installed.
- 🔐 Access to a completed Evalify quiz result page.
- 🧠 AEGIS-MIND installed and running locally.
- 🗺️ Syllabus topics added in **Syllabus Mapping** for best topic classification.

Supported Evalify URL pattern:

```text
http://v1.evalify.amritanet.edu/student/quiz/result/*
```

If your result page uses HTTPS, see the HTTPS note in [Step 2](#step-2-install-the-exporter-script).

---

## 🧩 Step 1: Install Tampermonkey

1. Open your browser's extension store.
2. Search for **Tampermonkey**.
3. Install the extension.
4. Pin Tampermonkey to your browser toolbar for easier access.

After installation, you should see the Tampermonkey icon in your toolbar or extensions menu.

---

## 📜 Step 2: Install The Exporter Script

1. Click the **Tampermonkey** extension icon.
2. Select **Create a new script**.
3. Delete the default template.
4. Open `tampermonkey_script.js` from this repository.
5. Paste the entire script into the Tampermonkey editor.
6. Save the script.

The script header should include:

```javascript
// @name         Evalify to AEGIS-MIND Exporter (v1.3)
// @match        http://v1.evalify.amritanet.edu/student/quiz/result/*
// @grant        GM_setClipboard
```

### HTTPS URL support

If your Evalify result page starts with `https://`, add this line inside the userscript metadata block:

```javascript
// @match        https://v1.evalify.amritanet.edu/student/quiz/result/*
```

Then save the script and refresh the Evalify page.

---

## 📤 Step 3: Export JSON From Evalify

1. Log in to Evalify.
2. Open the completed quiz result you want to import.
3. Wait until all question result blocks finish loading.
4. Look for the purple **Copy JSON for AEGIS-MIND** button near the top-right corner.
5. Click the button.
6. Confirm the browser alert says something like:

```text
Exported 20 questions. Coding answers and variable marks are now included!
```

The JSON is now copied to your clipboard.

---

## 🧠 Step 4: Open AEGIS-MIND

From the project root, run:

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m streamlit run app.py
```

macOS/Linux:

```bash
source .venv/bin/activate
python -m streamlit run app.py
```

On Windows, you can also use the included launcher:

```powershell
.\run_app.bat
```

Always launch through the project `.venv` so AEGIS-MIND uses the dependencies from `requirements.txt`. Then open the **Import Evalify** page from the Streamlit sidebar.

---

## 🧾 Step 5: Paste, Preview, And Tag

Paste the copied JSON into the import text area. AEGIS-MIND will immediately:

- validate the JSON structure
- filter out non-MCQ questions
- warn about duplicate Evalify test IDs
- load your existing syllabus topics
- auto-classify each MCQ into the closest topic
- show a preview table of questions, options, outcomes, and correct answers

Before importing, fill in:

| Field | Purpose |
| :--- | :--- |
| **Test Date** | Session date saved into `Behavioural_Log`. |
| **Default Difficulty Level** | Difficulty assigned to imported MCQs. |
| **Hours Slept Last Night** | Used by behavioral diagnostics. |
| **Stress Level** | Used by stress/accuracy correlation analysis. |
| **Topic Tags** | Auto-filled, but manually adjustable before import. |

> Tip: Add syllabus topics before importing. Topic classification works best when the syllabus map is already present.

---

## ✅ Step 6: Import And Diagnose

1. Keep **Run diagnostics after import** enabled if you want the dashboard updated immediately.
2. Click **Import Test**.
3. Wait for the success message showing:
   - Internal Test ID
   - External Evalify Test ID
   - Number of MCQs imported
4. Open **Dashboard** or **Diagnostic Report** to review updated insights.

Imported Evalify questions are stored with:

```text
Source = evalify
External_Test_ID = <Evalify quiz result ID>
```

---

## 🗃️ Database Writes

The importer updates the following local SQLite tables:

| Table | What Gets Stored |
| :--- | :--- |
| `Students` | Ensures the default student exists. |
| `Behavioural_Log` | Test date, sleep hours, stress level, and internal test ID. |
| `Questions` | Imported MCQs, options, answers, source, and external test ID. |
| `Student_Profile` | Ensures each imported topic has a profile row. |
| `Academic_Performance_Log` | Outcome, topic tag, sequence number, and difficulty. |

---

## 🧪 Exported JSON Shape

The Tampermonkey script exports a list of question objects similar to:

```json
{
  "student_id": 1,
  "test_id": "evalify-result-id",
  "topic_tag": null,
  "question_id": 1,
  "question_text": "Question text",
  "options": ["A) First option", "B) Second option"],
  "correct_answer": "A",
  "outcome": 1,
  "time_spent_seconds": null,
  "difficulty_level": null,
  "test_sequence_number": 1,
  "time_of_day": null,
  "sleep_hours": null,
  "stress_level": null
}
```

AEGIS-MIND fills or overrides topic tags, difficulty level, sleep hours, stress level, and session date during import.

---

## 🛟 Troubleshooting

| Problem | Fix |
| :--- | :--- |
| Button does not appear | Confirm Tampermonkey and the script are enabled, then refresh the Evalify result page. |
| URL does not match | Add the HTTPS `@match` line if your page uses `https://`. |
| `No quiz questions detected` | Make sure you are on the completed quiz result page and wait for content to load. |
| Invalid JSON in AEGIS-MIND | Click the export button again and paste directly without editing. |
| All questions filtered out | The test likely contains coding/descriptive questions only; importer currently accepts MCQs. |
| Topic tags look wrong | Add better syllabus topics or manually override tags before importing. |
| Duplicate warning appears | The same Evalify test ID already exists; continuing may skew diagnostics. |

---

## 🔐 Privacy Notes

- The userscript only runs on the configured Evalify quiz result URL pattern.
- Exported data is copied to your clipboard; it is not sent to an external server by the script.
- Import happens locally inside AEGIS-MIND.
- Imported records are stored in `student_helper.db`.

---

<div align="center">

**Evalify results become actionable AEGIS-MIND diagnostics in one copy-paste workflow.**

</div>
