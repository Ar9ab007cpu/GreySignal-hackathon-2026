import os
from typing import Any, Dict

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("GREYSIGNAL_API_URL", "http://127.0.0.1:8000")


st.set_page_config(
    page_title="GreySignal",
    page_icon="GS",
    layout="wide",
)


def risk_color(score: float) -> str:
    if score < 35:
        return "#17803d"
    if score < 60:
        return "#b7791f"
    if score < 78:
        return "#c2410c"
    return "#b91c1c"


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
        return ["Vietnam", "India", "Indonesia", "Mexico", "Germany"]


def render_gauge(score: float) -> go.Figure:
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            number={"suffix": "/100", "font": {"size": 34}},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": risk_color(score)},
                "steps": [
                    {"range": [0, 35], "color": "#dff3e6"},
                    {"range": [35, 60], "color": "#fff1cf"},
                    {"range": [60, 78], "color": "#ffdfc2"},
                    {"range": [78, 100], "color": "#ffd6d6"},
                ],
            },
        )
    )
    fig.update_layout(
        height=260,
        margin={"l": 20, "r": 20, "t": 20, "b": 20},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#f8fafc"},
    )
    return fig


st.markdown(
    """
    <style>
    .block-container { padding-top: 2rem; }
    div[data-testid="stMetric"] {
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 14px 16px;
        background: #111827;
        min-height: 78px;
    }
    div[data-testid="stMetric"] label,
    div[data-testid="stMetric"] [data-testid="stMetricLabel"] {
        color: #cbd5e1;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #f8fafc;
        font-weight: 700;
        line-height: 1.15;
    }
    h1 {
        line-height: 1.2;
    }
    .gs-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 18px;
        padding: 14px 18px;
        margin-bottom: 18px;
        border: 1px solid #263241;
        border-radius: 8px;
        background: #0f172a;
    }
    .gs-brand {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .gs-logo {
        position: relative;
        width: 42px;
        height: 42px;
        border-radius: 10px;
        background: #111827;
        border: 1px solid #475569;
        box-shadow: inset 0 0 0 1px rgba(248,250,252,0.04);
        overflow: hidden;
    }
    .gs-logo::before {
        content: "";
        position: absolute;
        width: 24px;
        height: 24px;
        left: 8px;
        top: 8px;
        border-radius: 50%;
        border: 2px solid #ef4444;
        box-shadow: 0 0 0 5px rgba(239,68,68,0.12);
    }
    .gs-logo::after {
        content: "";
        position: absolute;
        width: 22px;
        height: 3px;
        left: 17px;
        top: 20px;
        border-radius: 999px;
        background: #f8fafc;
        transform: rotate(-28deg);
        transform-origin: left center;
    }
    .gs-logo-dot {
        position: absolute;
        width: 7px;
        height: 7px;
        right: 8px;
        top: 10px;
        border-radius: 50%;
        background: #ef4444;
    }
    .gs-title {
        font-size: 1.25rem;
        font-weight: 800;
        color: #f8fafc;
        line-height: 1;
    }
    .gs-subtitle {
        margin-top: 4px;
        color: #94a3b8;
        font-size: 0.85rem;
    }
    .gs-status {
        color: #cbd5e1;
        font-size: 0.85rem;
        white-space: nowrap;
    }
    .gs-footer {
        margin-top: 36px;
        padding: 18px 0 6px;
        border-top: 1px solid #263241;
        color: #94a3b8;
        font-size: 0.85rem;
        display: grid;
        grid-template-columns: 1fr 1.4fr 1fr;
        gap: 16px;
    }
    .gs-footer strong {
        color: #e2e8f0;
        display: block;
        margin-bottom: 4px;
    }
    .gs-doc-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 14px;
        margin-top: 18px;
    }
    .gs-doc-panel {
        border: 1px solid #263241;
        border-radius: 8px;
        padding: 14px;
        background: #0f172a;
        min-height: 130px;
        transition: transform 160ms ease, border-color 160ms ease, box-shadow 160ms ease, background 160ms ease;
    }
    .gs-doc-panel h4 {
        color: #f8fafc;
        margin: 0 0 8px 0;
        font-size: 0.98rem;
        transition: color 160ms ease;
    }
    .gs-doc-panel p {
        color: #cbd5e1;
        margin: 0;
        font-size: 0.9rem;
        line-height: 1.45;
    }
    .gs-doc-panel:hover {
        transform: translateY(-3px);
        border-color: #ef4444;
        background: #111827;
        box-shadow: 0 12px 28px rgba(0,0,0,0.22);
    }
    .gs-doc-panel:hover h4 {
        color: #fecaca;
    }
    .gs-doc-note {
        margin-top: 16px;
        padding: 14px;
        border-left: 3px solid #ef4444;
        background: #111827;
        color: #cbd5e1;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="gs-header">
        <div class="gs-brand">
            <div class="gs-logo"><span class="gs-logo-dot"></span></div>
            <div>
                <div class="gs-title">GreySignal</div>
                <div class="gs-subtitle">Geopolitical business risk intelligence</div>
            </div>
        </div>
        <div class="gs-status">Local intelligence workspace</div>
    </div>
    """,
    unsafe_allow_html=True,
)


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

STEPS = [
    "Market",
    "Investment",
    "Exposure",
    "Data",
    "Review",
]


def set_step(step: int) -> None:
    st.session_state.wizard_step = max(0, min(step, len(STEPS) - 1))


def select_index(options: list[str], value: str) -> int:
    return options.index(value) if value in options else 0


submitted = False
form = st.session_state.assessment_form
step = st.session_state.wizard_step

wizard_left, wizard_center, wizard_right = st.columns([0.8, 1.4, 0.8])
with wizard_center:
    st.subheader("Assessment")
    st.progress((step + 1) / len(STEPS))
    st.caption(f"Step {step + 1} of {len(STEPS)}: {STEPS[step]}")

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
        review_df = pd.DataFrame([{"Question": key, "Answer": value} for key, value in review_rows.items()])
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

score = assessment["overall_score"]
rating = assessment["rating"]
recommendation = assessment["recommendation"]

top_left, top_right = st.columns([1, 1.4])
with top_left:
    st.plotly_chart(render_gauge(score), use_container_width=True)
with top_right:
    metric_cols = st.columns(3)
    metric_cols[0].metric("Country", assessment["country"])
    metric_cols[1].metric("Risk rating", rating)
    metric_cols[2].metric("Score", f"{score}/100")
    st.subheader("Recommendation")
    st.write(recommendation)
    st.write(assessment["summary"])

st.divider()

factor_df = pd.DataFrame(assessment["factors"])
factor_df["weighted_contribution"] = factor_df["score"] * factor_df["weight"]

left, right = st.columns([1.1, 1])
with left:
    st.subheader("Risk factors")
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
        )
    )
    fig.update_layout(
        xaxis_title="Risk score",
        yaxis_title="",
        xaxis={"range": [0, 100]},
        height=360,
        margin={"l": 10, "r": 10, "t": 20, "b": 40},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#f8fafc"},
    )
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Supporting evidence")
evidence_df = pd.DataFrame(assessment["evidence"])
st.dataframe(evidence_df, use_container_width=True, hide_index=True)

details_tabs = st.tabs(
    [
        "AI brief",
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
    st.subheader("Workflow")
    for step in assessment.get("workflow_steps", []):
        st.write(f"- {step}")

with details_tabs[1]:
    st.dataframe(pd.DataFrame(assessment.get("agent_outputs", [])), use_container_width=True, hide_index=True)

with details_tabs[2]:
    st.dataframe(pd.DataFrame(assessment.get("retrieval_results", [])), use_container_width=True, hide_index=True)

with details_tabs[3]:
    st.write("Sentiment")
    st.json(assessment.get("sentiment", {}))
    st.write("Extracted event signals")
    st.dataframe(pd.DataFrame(assessment.get("event_signals", [])), use_container_width=True, hide_index=True)

with details_tabs[4]:
    st.dataframe(pd.DataFrame(assessment.get("forecasts", [])), use_container_width=True, hide_index=True)

with details_tabs[5]:
    model_cols = st.columns(2)
    with model_cols[0]:
        st.write("Model outputs")
        st.json(assessment.get("model_outputs", {}))
    with model_cols[1]:
        st.write("SHAP explanation")
        st.json(assessment.get("shap_explanation", {}))
        st.write("Confidence interval")
        st.json(assessment.get("confidence_interval", {}))

with details_tabs[6]:
    graph = assessment.get("knowledge_graph", {})
    st.metric("Graph nodes", len(graph.get("nodes", [])))
    st.metric("Graph edges", len(graph.get("edges", [])))
    st.json(
        {
            "nodes": graph.get("nodes", [])[:20],
            "edges": graph.get("edges", [])[:20],
        }
    )

with st.expander("Raw assessment JSON"):
    st.json(assessment)

render_footer()
