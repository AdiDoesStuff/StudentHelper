import streamlit as st
from core.db.database_init import init_db

st.set_page_config(
    page_title="AEGIS-MIND — Adaptive Learning Diagnostics",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()  # Safe to call repeatedly — uses CREATE IF NOT EXISTS

# Single-student mode
st.session_state["student_id"] = 1

# ── Hero Landing Page ──────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* Global font override */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Hero section */
.hero-wrapper {
    background: linear-gradient(135deg, #0f0c29 0%, #1a1a4e 40%, #24243e 100%);
    border-radius: 20px;
    padding: 60px 48px 52px 48px;
    margin-bottom: 40px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 20px 60px rgba(0,0,0,0.5);
}
.hero-wrapper::before {
    content: "";
    position: absolute;
    top: -80px; right: -80px;
    width: 360px; height: 360px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(100,108,255,0.25) 0%, transparent 70%);
    pointer-events: none;
}
.hero-wrapper::after {
    content: "";
    position: absolute;
    bottom: -60px; left: -60px;
    width: 280px; height: 280px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(0,200,255,0.15) 0%, transparent 70%);
    pointer-events: none;
}
.hero-badge {
    display: inline-block;
    background: rgba(100,108,255,0.2);
    border: 1px solid rgba(100,108,255,0.5);
    color: #a5b4fc;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 5px 14px;
    border-radius: 100px;
    margin-bottom: 20px;
}
.hero-title {
    font-size: clamp(2.6rem, 5vw, 4rem);
    font-weight: 800;
    line-height: 1.1;
    background: linear-gradient(90deg, #ffffff 0%, #a5b4fc 50%, #67e8f9 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 16px 0;
}
.hero-subtitle {
    font-size: 1.15rem;
    color: #94a3b8;
    max-width: 580px;
    line-height: 1.7;
    margin-bottom: 36px;
}
.hero-stats {
    display: flex;
    gap: 32px;
    flex-wrap: wrap;
}
.hero-stat {
    text-align: center;
}
.hero-stat-value {
    font-size: 1.9rem;
    font-weight: 700;
    color: #a5b4fc;
    line-height: 1;
}
.hero-stat-label {
    font-size: 0.78rem;
    color: #64748b;
    font-weight: 500;
    letter-spacing: 0.5px;
    margin-top: 4px;
    text-transform: uppercase;
}

/* Section headings */
.section-heading {
    font-size: 1.35rem;
    font-weight: 700;
    color: #e2e8f0;
    margin-bottom: 4px;
}
.section-sub {
    font-size: 0.9rem;
    color: #64748b;
    margin-bottom: 22px;
}

/* Feature cards */
.feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 16px;
    margin-bottom: 40px;
}
.feature-card {
    background: linear-gradient(145deg, #1e2235, #16192a);
    border: 1px solid rgba(100,108,255,0.15);
    border-radius: 16px;
    padding: 22px 20px;
    transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    cursor: default;
}
.feature-card:hover {
    transform: translateY(-4px);
    border-color: rgba(100,108,255,0.45);
    box-shadow: 0 12px 32px rgba(100,108,255,0.15);
}
.feature-icon {
    font-size: 2rem;
    margin-bottom: 10px;
    display: block;
}
.feature-title {
    font-size: 1rem;
    font-weight: 700;
    color: #e2e8f0;
    margin-bottom: 6px;
}
.feature-desc {
    font-size: 0.83rem;
    color: #64748b;
    line-height: 1.6;
}

/* Workflow steps */
.workflow {
    display: flex;
    gap: 0;
    flex-wrap: wrap;
    margin-bottom: 40px;
}
.workflow-step {
    flex: 1;
    min-width: 140px;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    position: relative;
    padding: 0 12px;
}
.workflow-step:not(:last-child)::after {
    content: "→";
    position: absolute;
    right: -10px;
    top: 18px;
    color: #4338ca;
    font-size: 1.2rem;
}
.workflow-num {
    width: 40px; height: 40px;
    border-radius: 50%;
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    color: white;
    font-size: 0.95rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 10px;
    box-shadow: 0 4px 12px rgba(79,70,229,0.4);
}
.workflow-label {
    font-size: 0.82rem;
    color: #94a3b8;
    font-weight: 500;
    line-height: 1.4;
}

/* Divider */
.divider {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.07);
    margin: 32px 0;
}

/* Footer */
.footer {
    text-align: center;
    color: #334155;
    font-size: 0.8rem;
    padding: 20px 0 10px;
}
</style>

<!-- Hero -->
<div class="hero-wrapper">
    <div class="hero-badge">🧠 AI-Powered Learning</div>
    <h1 class="hero-title">AEGIS-MIND</h1>
    <p class="hero-subtitle">
        Your personal adaptive study companion. AEGIS-MIND diagnoses knowledge gaps,
        generates AI-crafted tests, and builds a personalized plan to maximize your score.
    </p>
    <div class="hero-stats">
        <div class="hero-stat">
            <div class="hero-stat-value">∞</div>
            <div class="hero-stat-label">Questions</div>
        </div>
        <div class="hero-stat">
            <div class="hero-stat-value">AI</div>
            <div class="hero-stat-label">Diagnostics</div>
        </div>
        <div class="hero-stat">
            <div class="hero-stat-value">24/7</div>
            <div class="hero-stat-label">Available</div>
        </div>
        <div class="hero-stat">
            <div class="hero-stat-value">100%</div>
            <div class="hero-stat-label">Personalized</div>
        </div>
    </div>
</div>

<!-- How It Works -->
<div class="section-heading">⚙️ How It Works</div>
<div class="section-sub">Follow this workflow to get the most out of AEGIS-MIND</div>
<div class="workflow">
    <div class="workflow-step">
        <div class="workflow-num">1</div>
        <div class="workflow-label">Map your Syllabus</div>
    </div>
    <div class="workflow-step">
        <div class="workflow-num">2</div>
        <div class="workflow-label">Upload Study Material</div>
    </div>
    <div class="workflow-step">
        <div class="workflow-num">3</div>
        <div class="workflow-label">Generate & Take Tests</div>
    </div>
    <div class="workflow-step">
        <div class="workflow-num">4</div>
        <div class="workflow-label">Review Diagnostics</div>
    </div>
    <div class="workflow-step">
        <div class="workflow-num">5</div>
        <div class="workflow-label">Revise Mistakes</div>
    </div>
    <div class="workflow-step">
        <div class="workflow-num">6</div>
        <div class="workflow-label">Get Your Study Plan</div>
    </div>
</div>

<hr class="divider">

<!-- Features -->
<div class="section-heading">✨ Features</div>
<div class="section-sub">Everything you need to study smarter, not harder</div>
<div class="feature-grid">
    <div class="feature-card">
        <span class="feature-icon">📊</span>
        <div class="feature-title">Smart Dashboard</div>
        <div class="feature-desc">Visual breakdown of your weakness index, topic performance, and study streaks at a glance.</div>
    </div>
    <div class="feature-card">
        <span class="feature-icon">🗺️</span>
        <div class="feature-title">Syllabus Mapping</div>
        <div class="feature-desc">Paste your syllabus and automatically build a prerequisite knowledge graph.</div>
    </div>
    <div class="feature-card">
        <span class="feature-icon">📄</span>
        <div class="feature-title">Document Upload</div>
        <div class="feature-desc">Upload PDFs and let local AI sort your notes into the right topic buckets automatically.</div>
    </div>
    <div class="feature-card">
        <span class="feature-icon">🎯</span>
        <div class="feature-title">AI Test Generation</div>
        <div class="feature-desc">Generate targeted MCQ tests powered by Gemini or Groq (Llama 3.3 70B).</div>
    </div>
    <div class="feature-card">
        <span class="feature-icon">📥</span>
        <div class="feature-title">Evalify Import</div>
        <div class="feature-desc">Import external Evalify test results directly into your diagnostic profile.</div>
    </div>
    <div class="feature-card">
        <span class="feature-icon">🔄</span>
        <div class="feature-title">Mistake Revision</div>
        <div class="feature-desc">Re-test exclusively on questions you got wrong to efficiently close knowledge gaps.</div>
    </div>
    <div class="feature-card">
        <span class="feature-icon">🔬</span>
        <div class="feature-title">Deep Diagnostics</div>
        <div class="feature-desc">Kurtosis analysis, knowledge-graph root causes, and sleep/stress correlation reports.</div>
    </div>
    <div class="feature-card">
        <span class="feature-icon">📅</span>
        <div class="feature-title">Personalized Planner</div>
        <div class="feature-desc">AI-generated 2-day study briefs tailored to your upcoming tests and weak areas.</div>
    </div>
</div>

<hr class="divider">
<div class="footer">AEGIS-MIND · Built for adaptive, data-driven student success</div>
""", unsafe_allow_html=True)
