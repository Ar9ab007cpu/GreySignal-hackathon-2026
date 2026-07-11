import os
from typing import Any, Dict

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("GREYSIGNAL_API_URL", "http://127.0.0.1:8010")

FALLBACK_COUNTRIES = [
    "Australia",
    "Bangladesh",
    "Brazil",
    "Canada",
    "China",
    "France",
    "Germany",
    "India",
    "Indonesia",
    "Italy",
    "Japan",
    "Malaysia",
    "Mexico",
    "Netherlands",
    "Pakistan",
    "Philippines",
    "Poland",
    "Saudi Arabia",
    "Singapore",
    "South Africa",
    "South Korea",
    "Spain",
    "Thailand",
    "Turkey",
    "United Arab Emirates",
    "United Kingdom",
    "United States",
    "Vietnam",
]


st.set_page_config(
    page_title="GreySignal  --  Geopolitical Risk Intelligence",
    page_icon="GS",
    layout="wide",
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def risk_color(score: float) -> str:
    if score < 35:
        return "#34d399"
    if score < 60:
        return "#fbbf24"
    if score < 78:
        return "#fb923c"
    return "#fb7185"


def risk_gradient(score: float) -> str:
    if score < 35:
        return "linear-gradient(135deg, #34d399, #6ee7b7)"
    if score < 60:
        return "linear-gradient(135deg, #f59e0b, #fbbf24)"
    if score < 78:
        return "linear-gradient(135deg, #f97316, #fb923c)"
    return "linear-gradient(135deg, #ef4444, #fb7185)"


def risk_bg(score: float) -> str:
    if score < 35:
        return "rgba(52, 211, 153, 0.07)"
    if score < 60:
        return "rgba(251, 191, 36, 0.07)"
    if score < 78:
        return "rgba(251, 146, 60, 0.07)"
    return "rgba(251, 113, 133, 0.07)"


def call_assessment(payload: Dict[str, Any]) -> Dict[str, Any]:
    response = requests.post(f"{API_URL}/assess", json=payload, timeout=45)
    response.raise_for_status()
    return response.json()


def get_countries() -> list[str]:
    try:
        response = requests.get(f"{API_URL}/countries", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return FALLBACK_COUNTRIES


def render_gauge(score: float) -> go.Figure:
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            number={
                "suffix": " / 100",
                "font": {"size": 36, "color": "#e2e8f0", "family": "Inter, sans-serif"},
            },
            gauge={
                "axis": {
                    "range": [0, 100],
                    "tickcolor": "rgba(148,163,184,0.3)",
                    "tickwidth": 1,
                    "dtick": 20,
                },
                "bar": {"color": risk_color(score), "thickness": 0.78},
                "bgcolor": "rgba(30, 41, 59, 0.35)",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 35], "color": "rgba(52, 211, 153, 0.06)"},
                    {"range": [35, 60], "color": "rgba(251, 191, 36, 0.06)"},
                    {"range": [60, 78], "color": "rgba(251, 146, 60, 0.06)"},
                    {"range": [78, 100], "color": "rgba(251, 113, 133, 0.06)"},
                ],
                "threshold": {
                    "line": {"color": "#e2e8f0", "width": 2},
                    "thickness": 0.78,
                    "value": score,
                },
            },
        )
    )
    fig.update_layout(
        height=280,
        margin={"l": 24, "r": 24, "t": 30, "b": 10},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#e2e8f0", "family": "Inter, sans-serif"},
    )
    return fig


# ---------------------------------------------------------------------------
# Global CSS  --  Premium dark theme
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    /* ===== GLOBAL FOUNDATION ===== */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    .stApp {
        background: linear-gradient(168deg, #0b1120 0%, #0f172a 40%, #1a1039 100%);
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1220px;
    }

    /* ===== SCROLLBAR ===== */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #334155; border-radius: 8px; }
    ::-webkit-scrollbar-thumb:hover { background: #475569; }

    /* ===== LINKS ===== */
    a { color: #818cf8 !important; text-decoration: none !important; }
    a:hover { color: #a5b4fc !important; }

    /* ===== DIVIDERS ===== */
    hr { border-color: rgba(148, 163, 184, 0.07) !important; }

    /* ===== HEADINGS ===== */
    h1, h2, h3, h4 {
        color: #f1f5f9 !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
    }
    h2 { font-size: 1.35rem !important; }
    h3 { font-size: 1.15rem !important; }

    /* ===== HEADER ===== */
    .gs-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        padding: 16px 26px;
        margin-bottom: 24px;
        border-radius: 16px;
        background: linear-gradient(
            135deg,
            rgba(99, 102, 241, 0.10) 0%,
            rgba(139, 92, 246, 0.07) 50%,
            rgba(6, 182, 212, 0.05) 100%
        );
        border: 1px solid rgba(99, 102, 241, 0.14);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
    }

    .gs-brand {
        display: flex;
        align-items: center;
        gap: 14px;
    }

    .gs-logo {
        position: relative;
        width: 44px;
        height: 44px;
        border-radius: 12px;
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 18px rgba(99, 102, 241, 0.30);
        flex-shrink: 0;
    }

    .gs-logo::before {
        content: "";
        position: absolute;
        width: 20px;
        height: 20px;
        border-radius: 50%;
        border: 2.5px solid rgba(255, 255, 255, 0.85);
    }

    .gs-logo::after {
        content: "";
        position: absolute;
        width: 16px;
        height: 2.5px;
        border-radius: 4px;
        background: rgba(255, 255, 255, 0.9);
        transform: rotate(-35deg) translate(5px, 3px);
    }

    .gs-title {
        font-size: 1.28rem;
        font-weight: 800;
        color: #f1f5f9;
        letter-spacing: -0.025em;
        line-height: 1;
    }

    .gs-subtitle {
        margin-top: 3px;
        color: #94a3b8;
        font-size: 0.8rem;
        font-weight: 400;
        letter-spacing: 0.01em;
    }

    .gs-status {
        display: flex;
        align-items: center;
        gap: 8px;
        color: #94a3b8;
        font-size: 0.8rem;
        font-weight: 500;
        white-space: nowrap;
    }

    .gs-status-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #34d399;
        box-shadow: 0 0 8px rgba(52, 211, 153, 0.5);
        animation: gs-pulse 2.4s ease-in-out infinite;
    }

    @keyframes gs-pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.45; }
    }

    /* ===== METRIC CARDS ===== */
    div[data-testid="stMetric"] {
        background: rgba(30, 41, 59, 0.45);
        border: 1px solid rgba(148, 163, 184, 0.07);
        border-radius: 14px;
        padding: 18px 20px;
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        transition: border-color 0.3s ease, transform 0.3s ease, box-shadow 0.3s ease;
        min-height: 82px;
    }

    div[data-testid="stMetric"]:hover {
        border-color: rgba(99, 102, 241, 0.18);
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    }

    div[data-testid="stMetric"] label,
    div[data-testid="stMetric"] [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-size: 0.72rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }

    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #e2e8f0 !important;
        font-weight: 700 !important;
        font-size: 1.25rem !important;
        line-height: 1.2;
    }

    /* ===== PROGRESS BAR ===== */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #6366f1, #8b5cf6, #06b6d4) !important;
        border-radius: 8px !important;
    }
    .stProgress > div > div > div {
        background: rgba(30, 41, 59, 0.45) !important;
        border-radius: 8px !important;
    }

    /* ===== FORM INPUTS ===== */
    .stSelectbox > div > div,
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: rgba(15, 23, 42, 0.55) !important;
        border: 1px solid rgba(148, 163, 184, 0.10) !important;
        border-radius: 10px !important;
        color: #e2e8f0 !important;
        font-family: 'Inter', sans-serif !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }

    .stSelectbox > div > div:hover,
    .stTextInput > div > div > input:hover,
    .stTextArea > div > div > textarea:hover {
        border-color: rgba(99, 102, 241, 0.25) !important;
    }

    .stSelectbox > div > div:focus-within,
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.10) !important;
    }

    .stSelectbox label,
    .stTextInput label,
    .stTextArea label,
    .stSlider label,
    .stCheckbox label {
        color: #cbd5e1 !important;
        font-size: 0.84rem !important;
        font-weight: 500 !important;
    }

    /* ===== BUTTONS ===== */
    .stButton > button {
        background: rgba(99, 102, 241, 0.08) !important;
        border: 1px solid rgba(99, 102, 241, 0.20) !important;
        border-radius: 10px !important;
        color: #c7d2fe !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.86rem !important;
        padding: 0.55rem 1.4rem !important;
        transition: all 0.28s cubic-bezier(0.4, 0, 0.2, 1) !important;
        letter-spacing: 0.01em;
    }

    .stButton > button:hover {
        background: rgba(99, 102, 241, 0.16) !important;
        border-color: rgba(99, 102, 241, 0.35) !important;
        color: #e0e7ff !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 16px rgba(99, 102, 241, 0.12) !important;
    }

    .stButton > button:active {
        transform: translateY(0px);
    }

    button[kind="primary"],
    button[data-testid="stBaseButton-primary"] {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        border: 1px solid rgba(139, 92, 246, 0.35) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.22) !important;
    }

    button[kind="primary"]:hover,
    button[data-testid="stBaseButton-primary"]:hover {
        background: linear-gradient(135deg, #818cf8, #a78bfa) !important;
        box-shadow: 0 6px 28px rgba(99, 102, 241, 0.32) !important;
        transform: translateY(-2px);
    }

    /* ===== TABS ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background: rgba(15, 23, 42, 0.45);
        border-radius: 12px;
        padding: 4px;
        border: 1px solid rgba(148, 163, 184, 0.06);
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px !important;
        color: #94a3b8 !important;
        font-weight: 500 !important;
        font-size: 0.82rem !important;
        padding: 8px 16px !important;
        transition: all 0.22s ease;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: #e2e8f0 !important;
        background: rgba(99, 102, 241, 0.06);
    }

    .stTabs [aria-selected="true"] {
        background: rgba(99, 102, 241, 0.14) !important;
        color: #c7d2fe !important;
    }

    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #6366f1 !important;
    }

    .stTabs [data-baseweb="tab-border"] {
        display: none;
    }

    /* ===== DATAFRAMES ===== */
    .stDataFrame {
        border-radius: 12px !important;
        overflow: hidden;
        border: 1px solid rgba(148, 163, 184, 0.06) !important;
    }

    /* ===== EXPANDER ===== */
    .streamlit-expanderHeader {
        background: rgba(30, 41, 59, 0.35) !important;
        border-radius: 10px !important;
        border: 1px solid rgba(148, 163, 184, 0.06) !important;
        color: #94a3b8 !important;
        font-weight: 500 !important;
    }

    [data-testid="stExpander"] {
        border: 1px solid rgba(148, 163, 184, 0.06) !important;
        border-radius: 12px !important;
        background: rgba(15, 23, 42, 0.3) !important;
    }

    /* ===== CAPTION ===== */
    .stCaption, [data-testid="stCaptionContainer"] {
        color: #64748b !important;
        font-size: 0.78rem !important;
    }

    /* ===== SLIDER ===== */
    .stSlider > div > div > div > div {
        background: #6366f1 !important;
    }
    .stSlider > div > div > div > div > div {
        background: #6366f1 !important;
        box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3) !important;
    }

    /* ===== ALERTS ===== */
    .stAlert {
        border-radius: 12px !important;
        border: 1px solid rgba(148, 163, 184, 0.08) !important;
    }

    /* ===== JSON VIEWER ===== */
    [data-testid="stJson"] {
        background: rgba(15, 23, 42, 0.4) !important;
        border-radius: 10px;
        border: 1px solid rgba(148, 163, 184, 0.06);
    }

    /* ===== STEP INDICATOR ===== */
    .gs-steps {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0;
        margin: 6px 0 22px;
        padding: 0 20px;
    }

    .gs-step-item {
        display: flex;
        align-items: center;
    }

    .gs-step-node {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 6px;
    }

    .gs-step-circle {
        width: 34px;
        height: 34px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.76rem;
        font-weight: 700;
        font-family: 'Inter', sans-serif;
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .gs-step-circle.active {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: #ffffff;
        box-shadow: 0 4px 18px rgba(99, 102, 241, 0.35);
    }

    .gs-step-circle.done {
        background: rgba(52, 211, 153, 0.12);
        color: #34d399;
        border: 1.5px solid rgba(52, 211, 153, 0.25);
    }

    .gs-step-circle.pending {
        background: rgba(30, 41, 59, 0.45);
        color: #475569;
        border: 1.5px solid rgba(148, 163, 184, 0.10);
    }

    .gs-step-label {
        font-size: 0.68rem;
        font-weight: 500;
        letter-spacing: 0.01em;
        white-space: nowrap;
        transition: color 0.25s ease;
    }

    .gs-step-label.active { color: #a5b4fc; }
    .gs-step-label.done   { color: #6ee7b7; }
    .gs-step-label.pending { color: #475569; }

    .gs-step-line {
        width: 52px;
        height: 2px;
        border-radius: 2px;
        margin: 0 2px;
        margin-bottom: 20px;
        transition: background 0.35s ease;
    }

    .gs-step-line.done    { background: linear-gradient(90deg, #34d399, rgba(52, 211, 153, 0.25)); }
    .gs-step-line.pending { background: rgba(148, 163, 184, 0.08); }

    /* ===== DOC PANELS ===== */
    .gs-doc-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 16px;
        margin-top: 22px;
    }

    .gs-doc-panel {
        background: rgba(30, 41, 59, 0.35);
        border: 1px solid rgba(148, 163, 184, 0.07);
        border-radius: 14px;
        padding: 22px;
        min-height: 140px;
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        transition: all 0.32s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }

    .gs-doc-panel::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: transparent;
        transition: background 0.32s ease;
    }

    .gs-doc-panel:hover {
        transform: translateY(-4px);
        border-color: rgba(99, 102, 241, 0.18);
        background: rgba(30, 41, 59, 0.55);
        box-shadow: 0 16px 48px rgba(0, 0, 0, 0.18);
    }

    .gs-doc-panel:hover::before {
        background: linear-gradient(90deg, #6366f1, #8b5cf6);
    }

    .gs-doc-panel h4 {
        color: #e2e8f0;
        margin: 0 0 10px 0;
        font-size: 0.95rem;
        font-weight: 700;
        transition: color 0.25s ease;
    }

    .gs-doc-panel:hover h4 { color: #c7d2fe; }

    .gs-doc-panel p {
        color: #94a3b8;
        margin: 0;
        font-size: 0.84rem;
        line-height: 1.6;
    }

    /* ===== DOC NOTE ===== */
    .gs-doc-note {
        margin-top: 22px;
        padding: 16px 22px;
        border-left: 3px solid #6366f1;
        background: rgba(99, 102, 241, 0.05);
        border-radius: 0 12px 12px 0;
        color: #94a3b8;
        font-size: 0.84rem;
        line-height: 1.6;
    }

    /* ===== FOOTER ===== */
    .gs-footer {
        margin-top: 44px;
        padding: 26px 0 10px;
        border-top: 1px solid rgba(148, 163, 184, 0.06);
        color: #64748b;
        font-size: 0.8rem;
        line-height: 1.6;
        display: grid;
        grid-template-columns: 1fr 1.4fr 1fr;
        gap: 24px;
    }

    .gs-footer strong {
        color: #94a3b8;
        display: block;
        margin-bottom: 6px;
        font-weight: 600;
        font-size: 0.84rem;
    }

    /* ===== RESULT HERO ===== */
    .gs-hero {
        background: rgba(30, 41, 59, 0.35);
        border: 1px solid rgba(148, 163, 184, 0.07);
        border-radius: 16px;
        padding: 24px 28px;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
    }

    .gs-hero-label {
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #64748b;
        margin-bottom: 8px;
    }

    .gs-hero-value {
        font-size: 1.1rem;
        font-weight: 700;
        color: #e2e8f0;
        line-height: 1.3;
    }

    .gs-score-pill {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.01em;
    }

    /* ===== SECTION TITLES ===== */
    .gs-section-label {
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        color: #64748b;
        margin-bottom: 14px;
        padding-bottom: 10px;
        border-bottom: 1px solid rgba(148, 163, 184, 0.06);
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.markdown(
    """
    <div class="gs-header">
        <div class="gs-brand">
            <div class="gs-logo"></div>
            <div>
                <div class="gs-title">GreySignal</div>
                <div class="gs-subtitle">Geopolitical business risk intelligence</div>
            </div>
        </div>
        <div class="gs-status">
            <span class="gs-status-dot"></span>
            Local intelligence workspace
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Footer helper
# ---------------------------------------------------------------------------

def render_footer() -> None:
    st.markdown(
        """
        <div class="gs-footer">
            <div>
                <strong>GreySignal</strong>
                Business expansion risk intelligence for country, sector, and supply-chain decisions.
            </div>
            <div>
                <strong>Evidence-led assessment</strong>
                Combines economic, political, trade, weather, currency, and news signals into a structured risk view.
            </div>
            <div>
                <strong>Decision support</strong>
                Designed to support early due diligence; final decisions should include expert, legal, and local review.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Wizard state
# ---------------------------------------------------------------------------

DEFAULT_FORM = {
    "country": "Vietnam",
    "sector": "Manufacturing expansion",
    "city_or_port": "Hai Phong",
    "investment_size": "Medium",
    "entry_mode": "Greenfield",
    "time_horizon": "12-24 months",
    "risk_tolerance": "Medium",
    "labor_intensity": "Medium",
    "supply_chain_dependence": "Medium",
    "regulatory_sensitivity": "Medium",
    "local_partner_available": False,
    "news_keywords": "strike OR protest OR election OR tariff OR supply chain",
    "base_currency": "USD",
    "target_currency": "VND",
    "hs_code": "TOTAL",
    "years": (2020, 2026),
}

if "assessment_form" not in st.session_state:
    st.session_state.assessment_form = DEFAULT_FORM.copy()
if "wizard_step" not in st.session_state:
    st.session_state.wizard_step = 0
if "assessment" not in st.session_state:
    st.session_state.assessment = None

STEPS = ["Market", "Investment", "Exposure", "Data", "Review"]


def set_step(step: int) -> None:
    st.session_state.wizard_step = max(0, min(step, len(STEPS) - 1))


def select_index(options: list[str], value: str) -> int:
    return options.index(value) if value in options else 0


# ---------------------------------------------------------------------------
# Step indicator (custom HTML)
# ---------------------------------------------------------------------------

def render_step_indicator(current: int) -> None:
    parts = []
    for i, name in enumerate(STEPS):
        if i < current:
            css = "done"
        elif i == current:
            css = "active"
        else:
            css = "pending"

        parts.append(
            f'<div class="gs-step-node">'
            f'  <div class="gs-step-circle {css}">{i + 1}</div>'
            f'  <div class="gs-step-label {css}">{name}</div>'
            f'</div>'
        )

        if i < len(STEPS) - 1:
            line_css = "done" if i < current else "pending"
            parts.append(f'<div class="gs-step-line {line_css}"></div>')

    html = '<div class="gs-steps">' + "".join(parts) + '</div>'
    st.markdown(html, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Wizard
# ---------------------------------------------------------------------------

submitted = False
form = st.session_state.assessment_form
step = st.session_state.wizard_step

wizard_left, wizard_center, wizard_right = st.columns([0.8, 1.4, 0.8])
with wizard_center:
    st.subheader("Assessment")
    render_step_indicator(step)

    if step == 0:
        countries = get_countries()
        form["country"] = st.selectbox("Target country", countries, index=select_index(countries, form["country"]))
        form["sector"] = st.text_input("Sector or decision", form["sector"])
        form["city_or_port"] = st.text_input("City or port", form["city_or_port"])

    elif step == 1:
        sizes = ["Small", "Medium", "Large"]
        modes = ["Exporting", "Joint venture", "Greenfield", "Acquisition"]
        horizons = ["0-6 months", "6-12 months", "12-24 months", "24+ months"]
        form["investment_size"] = st.selectbox("Investment size", sizes, index=select_index(sizes, form["investment_size"]))
        form["entry_mode"] = st.selectbox("Entry mode", modes, index=select_index(modes, form["entry_mode"]))
        form["time_horizon"] = st.selectbox("Time horizon", horizons, index=select_index(horizons, form["time_horizon"]))
        form["risk_tolerance"] = st.selectbox("Risk tolerance", sizes, index=select_index(sizes, form["risk_tolerance"]))

    elif step == 2:
        levels = ["Low", "Medium", "High"]
        form["labor_intensity"] = st.selectbox("Labor intensity", levels, index=select_index(levels, form["labor_intensity"]))
        form["supply_chain_dependence"] = st.selectbox(
            "Supply-chain dependence",
            levels,
            index=select_index(levels, form["supply_chain_dependence"]),
        )
        form["regulatory_sensitivity"] = st.selectbox(
            "Regulatory sensitivity",
            levels,
            index=select_index(levels, form["regulatory_sensitivity"]),
        )
        form["local_partner_available"] = st.checkbox("Local partner available", value=form["local_partner_available"])

    elif step == 3:
        currencies = ["USD", "EUR", "GBP", "INR"]
        form["base_currency"] = st.selectbox(
            "Base currency",
            currencies,
            index=select_index(currencies, form["base_currency"]),
        )
        form["target_currency"] = st.text_input("Target currency", form["target_currency"], max_chars=3).upper()
        form["hs_code"] = st.text_input("HS code", form["hs_code"])
        form["years"] = st.slider("World Bank year range", 2015, 2026, form["years"])
        form["news_keywords"] = st.text_area("News keywords", form["news_keywords"], height=80)

    else:
        review_rows = {
            "Country": form["country"],
            "Sector": form["sector"],
            "City/port": form["city_or_port"],
            "Investment": form["investment_size"],
            "Entry mode": form["entry_mode"],
            "Time horizon": form["time_horizon"],
            "Risk tolerance": form["risk_tolerance"],
            "Supply-chain": form["supply_chain_dependence"],
            "Regulatory": form["regulatory_sensitivity"],
            "Currencies": f"{form['base_currency']} -> {form['target_currency']}",
        }
        review_df = pd.DataFrame([{"Parameter": key, "Value": value} for key, value in review_rows.items()])
        st.dataframe(review_df, use_container_width=True, hide_index=True)
        submitted = st.button("Start assessment", type="primary", use_container_width=True)

    nav_left, nav_right = st.columns(2)
    if nav_left.button("Back", use_container_width=True, disabled=step == 0):
        set_step(step - 1)
        st.rerun()
    if nav_right.button("Next", use_container_width=True, disabled=step == len(STEPS) - 1):
        set_step(step + 1)
        st.rerun()

st.divider()


# ---------------------------------------------------------------------------
# Run assessment
# ---------------------------------------------------------------------------

if submitted:
    form = st.session_state.assessment_form
    payload = {
        "country": form["country"],
        "sector": form["sector"],
        "city_or_port": form["city_or_port"],
        "investment_size": form["investment_size"],
        "entry_mode": form["entry_mode"],
        "time_horizon": form["time_horizon"],
        "risk_tolerance": form["risk_tolerance"],
        "labor_intensity": form["labor_intensity"],
        "supply_chain_dependence": form["supply_chain_dependence"],
        "regulatory_sensitivity": form["regulatory_sensitivity"],
        "local_partner_available": form["local_partner_available"],
        "news_keywords": form["news_keywords"],
        "base_currency": form["base_currency"],
        "target_currency": form["target_currency"],
        "hs_code": form["hs_code"],
        "start_year": form["years"][0],
        "end_year": form["years"][1],
    }
    with st.spinner("Collecting public signals and scoring risk..."):
        try:
            st.session_state.assessment = call_assessment(payload)
        except requests.RequestException as exc:
            st.error(f"Assessment failed. Check that the FastAPI backend is running. Detail: {exc}")

assessment = st.session_state.assessment


# ---------------------------------------------------------------------------
# Landing documentation (shown when no assessment exists)
# ---------------------------------------------------------------------------

if not assessment:
    doc_left, doc_center, doc_right = st.columns([0.45, 1.6, 0.45])
    with doc_center:
        st.subheader("GreySignal Overview")
        st.write(
            "GreySignal is a decision-support workspace for evaluating geopolitical and business risk before "
            "entering or expanding in a market. It combines real macroeconomic data, governance indicators, "
            "currency signals, weather exposure, trade context, and news/event monitoring into a single assessment."
        )
        st.markdown(
            """
            <div class="gs-doc-grid">
                <div class="gs-doc-panel">
                    <h4>What It Answers</h4>
                    <p>Whether a company should proceed, delay, or redesign an expansion plan based on country risk, operating exposure, and business fit.</p>
                </div>
                <div class="gs-doc-panel">
                    <h4>Evidence Used</h4>
                    <p>World Bank WDI/WGI, exchange rates, Open-Meteo weather signals, GDELT news, UN Comtrade trade data, and user-provided operating context.</p>
                </div>
                <div class="gs-doc-panel">
                    <h4>Analysis Produced</h4>
                    <p>Risk score, recommendation, AI executive brief, agent findings, forecasts, SHAP explanation, MAPIE confidence interval, and knowledge graph.</p>
                </div>
                <div class="gs-doc-panel">
                    <h4>Workflow</h4>
                    <p>LangGraph coordinates assessment initialization, evidence collection, validation, scoring, model explanation, and final response generation.</p>
                </div>
                <div class="gs-doc-panel">
                    <h4>Machine Learning</h4>
                    <p>XGBoost, CatBoost, and LightGBM train from a real country-year dataset built from World Bank WDI and WGI indicators.</p>
                </div>
                <div class="gs-doc-panel">
                    <h4>How To Use</h4>
                    <p>Complete the guided questions above. On the review step, select Start assessment. This documentation will be replaced by the results.</p>
                </div>
            </div>
            <div class="gs-doc-note">
                GreySignal is designed for early-stage decision intelligence. It does not replace legal, compliance, security, or in-country expert due diligence.
            </div>
            """,
            unsafe_allow_html=True,
        )
    render_footer()
    st.stop()


# ---------------------------------------------------------------------------
# Assessment results
# ---------------------------------------------------------------------------

score = assessment["overall_score"]
rating = assessment["rating"]
recommendation = assessment["recommendation"]

# -- Hero section --
top_left, top_right = st.columns([1, 1.4])
with top_left:
    st.plotly_chart(render_gauge(score), use_container_width=True)
with top_right:
    metric_cols = st.columns(3)
    metric_cols[0].metric("Country", assessment["country"])
    metric_cols[1].metric("Risk rating", rating)
    metric_cols[2].metric("Score", f"{score}/100")
    st.markdown('<div class="gs-section-label">Recommendation</div>', unsafe_allow_html=True)
    st.write(recommendation)
    st.write(assessment["summary"])

st.divider()

# -- Risk factors --
factor_df = pd.DataFrame(assessment["factors"])
factor_df["weighted_contribution"] = factor_df["score"] * factor_df["weight"]

left, right = st.columns([1.1, 1])
with left:
    st.markdown('<div class="gs-section-label">Risk Factors</div>', unsafe_allow_html=True)
    st.dataframe(
        factor_df[["name", "score", "weight", "weighted_contribution", "rationale"]],
        use_container_width=True,
        hide_index=True,
    )

with right:
    fig = go.Figure(
        go.Bar(
            x=factor_df["score"],
            y=factor_df["name"],
            orientation="h",
            marker_color=[risk_color(value) for value in factor_df["score"]],
            marker_line_width=0,
        )
    )
    fig.update_layout(
        xaxis_title="Risk score",
        yaxis_title="",
        xaxis={"range": [0, 100], "gridcolor": "rgba(148,163,184,0.06)"},
        yaxis={"gridcolor": "rgba(148,163,184,0.06)"},
        height=360,
        margin={"l": 10, "r": 10, "t": 20, "b": 40},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#94a3b8", "family": "Inter, sans-serif", "size": 12},
    )
    st.plotly_chart(fig, use_container_width=True)

# -- Evidence --
st.markdown('<div class="gs-section-label">Supporting Evidence</div>', unsafe_allow_html=True)
evidence_df = pd.DataFrame(assessment["evidence"])
st.dataframe(evidence_df, use_container_width=True, hide_index=True)

# -- Detail tabs --
details_tabs = st.tabs(
    [
        "AI Brief",
        "Agents",
        "Retrieval",
        "Events",
        "Forecasts",
        "Models",
        "Graph",
    ]
)

with details_tabs[0]:
    ai_summary = assessment.get("ai_summary") or "AI summary is not available. Check GROQ_API_KEY in .env."
    st.write(ai_summary)
    st.markdown('<div class="gs-section-label">Workflow</div>', unsafe_allow_html=True)
    for wf_step in assessment.get("workflow_steps", []):
        st.write(f"- {wf_step}")

with details_tabs[1]:
    st.dataframe(pd.DataFrame(assessment.get("agent_outputs", [])), use_container_width=True, hide_index=True)

with details_tabs[2]:
    st.dataframe(pd.DataFrame(assessment.get("retrieval_results", [])), use_container_width=True, hide_index=True)

with details_tabs[3]:
    st.markdown('<div class="gs-section-label">Sentiment</div>', unsafe_allow_html=True)
    st.json(assessment.get("sentiment", {}))
    st.markdown('<div class="gs-section-label">Extracted Event Signals</div>', unsafe_allow_html=True)
    st.dataframe(pd.DataFrame(assessment.get("event_signals", [])), use_container_width=True, hide_index=True)

with details_tabs[4]:
    st.dataframe(pd.DataFrame(assessment.get("forecasts", [])), use_container_width=True, hide_index=True)

with details_tabs[5]:
    model_cols = st.columns(2)
    with model_cols[0]:
        st.markdown('<div class="gs-section-label">Model Outputs</div>', unsafe_allow_html=True)
        st.json(assessment.get("model_outputs", {}))
    with model_cols[1]:
        st.markdown('<div class="gs-section-label">SHAP Explanation</div>', unsafe_allow_html=True)
        st.json(assessment.get("shap_explanation", {}))
        st.markdown('<div class="gs-section-label">Confidence Interval</div>', unsafe_allow_html=True)
        st.json(assessment.get("confidence_interval", {}))

with details_tabs[6]:
    graph = assessment.get("knowledge_graph", {})
    graph_cols = st.columns(2)
    graph_cols[0].metric("Graph nodes", len(graph.get("nodes", [])))
    graph_cols[1].metric("Graph edges", len(graph.get("edges", [])))
    st.json(
        {
            "nodes": graph.get("nodes", [])[:20],
            "edges": graph.get("edges", [])[:20],
        }
    )

with st.expander("Raw assessment JSON"):
    st.json(assessment)

render_footer()
