import streamlit as st


def apply_theme() -> None:
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --bg: #07090d;
    --panel: #10141c;
    --panel-soft: #151a24;
    --panel-warm: #1b1213;
    --line: rgba(255, 255, 255, 0.10);
    --line-strong: rgba(248, 113, 113, 0.36);
    --text: #f8fafc;
    --muted: #94a3b8;
    --muted-2: #64748b;
    --red: #ef4444;
    --red-hot: #fb7185;
    --amber: #f59e0b;
    --cyan: #22d3ee;
    --green: #34d399;
}

html, body, [class*="css"] {
    font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.stApp {
    color: var(--text);
    background:
        linear-gradient(140deg, rgba(127, 29, 29, 0.30) 0%, rgba(7, 9, 13, 0.95) 34%, rgba(4, 12, 20, 0.98) 100%),
        var(--bg);
}

.block-container {
    max-width: 1240px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1118 0%, #120d10 100%);
    border-right: 1px solid var(--line);
}

section[data-testid="stSidebar"] * {
    color: #dbeafe;
}

h1, h2, h3 {
    color: var(--text);
    letter-spacing: 0;
}

p, li, label, .stMarkdown, [data-testid="stMarkdownContainer"] {
    color: #cbd5e1;
}

.aegis-page-hero {
    border: 1px solid var(--line-strong);
    border-radius: 8px;
    padding: 28px 30px;
    margin: 0 0 28px;
    background:
        linear-gradient(135deg, rgba(185, 28, 28, 0.34), rgba(15, 23, 42, 0.68) 48%, rgba(8, 47, 73, 0.42)),
        linear-gradient(180deg, rgba(255, 255, 255, 0.06), rgba(255, 255, 255, 0.02));
    box-shadow: 0 20px 45px rgba(0, 0, 0, 0.34);
}

.aegis-kicker {
    color: #fecaca;
    font-size: 0.78rem;
    font-weight: 800;
    text-transform: uppercase;
    margin-bottom: 8px;
}

.aegis-page-title {
    color: #ffffff;
    font-size: clamp(2rem, 4vw, 3.4rem);
    font-weight: 800;
    line-height: 1.06;
    margin: 0;
}

.aegis-page-subtitle {
    color: #cbd5e1;
    font-size: 1rem;
    line-height: 1.65;
    max-width: 780px;
    margin: 14px 0 0;
}

.aegis-section-label {
    border-left: 4px solid var(--red-hot);
    padding-left: 12px;
    color: #fee2e2;
    font-weight: 800;
    margin: 28px 0 14px;
}

.aegis-divider {
    height: 1px;
    background: linear-gradient(90deg, rgba(248, 113, 113, 0), rgba(248, 113, 113, 0.55), rgba(34, 211, 238, 0.18), rgba(248, 113, 113, 0));
    margin: 28px 0;
}

div[data-testid="stMetric"],
div[data-testid="stForm"],
div[data-testid="stExpander"],
div[data-testid="stDataFrame"],
div[data-testid="stTable"],
div[data-testid="stFileUploader"],
div[data-testid="stAlert"] {
    border-radius: 8px !important;
}

div[data-testid="stMetric"] {
    background: linear-gradient(145deg, rgba(21, 26, 36, 0.96), rgba(27, 18, 19, 0.94));
    border: 1px solid var(--line);
    padding: 18px;
    box-shadow: 0 12px 26px rgba(0, 0, 0, 0.22);
}

div[data-testid="stMetricValue"] {
    color: #ffffff;
}

div[data-testid="stMetricLabel"] {
    color: #fecaca;
    font-weight: 700;
}

div[data-testid="stForm"],
div[data-testid="stExpander"],
div[data-testid="stFileUploader"] {
    background: rgba(16, 20, 28, 0.78);
    border: 1px solid var(--line);
}

.stButton > button,
.stDownloadButton > button,
button[kind="primary"] {
    border-radius: 8px !important;
    border: 1px solid rgba(248, 113, 113, 0.55) !important;
    background: linear-gradient(135deg, #dc2626, #991b1b) !important;
    color: #ffffff !important;
    font-weight: 800 !important;
    box-shadow: 0 12px 24px rgba(220, 38, 38, 0.24);
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    border-color: rgba(34, 211, 238, 0.65) !important;
    transform: translateY(-1px);
}

div[data-baseweb="select"] > div,
textarea,
input,
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stDateInput"] input,
[data-testid="stTimeInput"] input {
    border-radius: 8px !important;
    border-color: rgba(255, 255, 255, 0.14) !important;
    background-color: rgba(15, 23, 42, 0.78) !important;
    color: #f8fafc !important;
}

div[data-testid="stDataFrame"],
div[data-testid="stTable"] {
    border: 1px solid var(--line);
    overflow: hidden;
}

.stProgress > div > div > div {
    background: linear-gradient(90deg, var(--red), var(--amber), var(--cyan));
}

.aegis-chip-row {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-top: 20px;
}

.aegis-chip {
    border: 1px solid rgba(255, 255, 255, 0.13);
    border-radius: 999px;
    padding: 7px 12px;
    color: #e2e8f0;
    background: rgba(15, 23, 42, 0.68);
    font-size: 0.84rem;
    font-weight: 700;
}

@media (max-width: 700px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }
    .aegis-page-hero {
        padding: 22px 18px;
    }
}
</style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str, kicker: str = "AEGIS-MIND") -> None:
    st.markdown(
        f"""
<div class="aegis-page-hero">
    <div class="aegis-kicker">{kicker}</div>
    <h1 class="aegis-page-title">{title}</h1>
    <p class="aegis-page-subtitle">{subtitle}</p>
</div>
        """,
        unsafe_allow_html=True,
    )


def section_label(label: str) -> None:
    st.markdown(f'<div class="aegis-section-label">{label}</div>', unsafe_allow_html=True)


def divider() -> None:
    st.markdown('<div class="aegis-divider"></div>', unsafe_allow_html=True)
