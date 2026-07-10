# GreySignal

**Evidence-led geopolitical and business expansion risk intelligence**

GreySignal is a decision-support platform for organizations evaluating whether, where, and how to enter or expand in an international market. It combines public economic, governance, currency, weather, trade, and news signals with the proposed investment's operating profile to produce an explainable country-risk assessment.

The application returns a 0-100 risk score, risk rating, action-oriented recommendation, factor-level reasoning, supporting evidence, specialist-agent findings, forecasts, model predictions, uncertainty bounds, explainability output, and a machine-readable knowledge graph through a guided Streamlit interface and FastAPI API.

> GreySignal supports early-stage due diligence. It does not replace legal, regulatory, compliance, security, financial, or in-country expert advice.

## Table of Contents

- [Problem Statement](#problem-statement)
- [Vision](#vision)
- [Mission](#mission)
- [Solution Overview](#solution-overview)
- [Key Capabilities](#key-capabilities)
- [How GreySignal Works](#how-greysignal-works)
- [Risk Methodology](#risk-methodology)
- [Data Sources](#data-sources)
- [Machine Learning and Intelligence Layers](#machine-learning-and-intelligence-layers)
- [Technology Stack and Libraries](#technology-stack-and-libraries)
- [System Architecture](#system-architecture)
- [Project Structure](#project-structure)
- [Supported Countries](#supported-countries)
- [Installation and Configuration](#installation-and-configuration)
- [Running the Application](#running-the-application)
- [Using the Dashboard](#using-the-dashboard)
- [API Reference](#api-reference)
- [Training Dataset](#training-dataset)
- [Reliability and Fallback Behavior](#reliability-and-fallback-behavior)
- [Limitations](#limitations)
- [Troubleshooting](#troubleshooting)
- [Responsible Use](#responsible-use)

## Problem Statement

International expansion decisions depend on information that is fragmented across economic databases, governance indicators, trade systems, weather services, news feeds, and internal business assumptions. Decision-makers often face four problems:

1. **Fragmented evidence:** relevant signals live in separate systems and use different formats, scales, and update schedules.
2. **Generic country ratings:** traditional country scores do not account for the proposed investment size, entry mode, time horizon, labor intensity, supply-chain dependence, regulatory sensitivity, or local partnerships.
3. **Limited explainability:** a single score is difficult to trust when the contributing evidence, model behavior, and uncertainty are not visible.
4. **Slow early-stage analysis:** manually collecting and comparing signals delays screening and can lead to inconsistent decisions.

GreySignal addresses this gap by turning public signals and business context into a structured, traceable, and repeatable assessment. It is designed to answer an initial strategic question:

> Should the organization proceed, proceed selectively, delay major commitments, or require executive-level risk acceptance for this market decision?

## Vision

To make geopolitical and market-entry risk intelligence accessible, transparent, and useful at the moment a business decision is being shaped.

GreySignal's long-term vision is a decision workspace where teams can continuously connect global events and country fundamentals to their specific operating exposure rather than relying only on static, generic country rankings.

## Mission

GreySignal's mission is to:

- unify credible public indicators in one assessment workflow;
- personalize country risk using the actual business and operating context;
- expose evidence, assumptions, model predictions, and uncertainty;
- remain useful when optional APIs are missing or temporarily unavailable;
- accelerate early-stage due diligence while preserving human review and accountability.

## Solution Overview

A user completes a five-step assessment wizard describing the target market and proposed operation. The backend then:

1. normalizes the country and loads its profile;
2. collects economic, governance, currency, weather, news, and trade evidence;
3. calculates interpretable factor-level rule scores;
4. creates specialist economic, political, trade, weather, and news findings;
5. runs XGBoost, CatBoost, and LightGBM regression models;
6. combines the ML ensemble with the business-fit score;
7. generates SHAP feature contributions and a MAPIE confidence interval;
8. runs BM25 retrieval, local hash embeddings, event extraction, sentiment scoring, and forecasting;
9. optionally creates an executive brief through Groq-hosted Llama;
10. builds a knowledge graph, validates the result through LangGraph, stores the assessment in SQLite, and returns the response.

## Key Capabilities

### Guided assessment

The Streamlit interface collects:

- target country, sector or decision, and city/port;
- investment size and market-entry mode;
- decision time horizon and risk tolerance;
- labor intensity, supply-chain dependence, and regulatory sensitivity;
- availability of a local partner;
- base and target currencies;
- HS code and analysis year range;
- configurable news-risk keywords.

### Evidence-based output

Each result includes source, label, value, availability status, and supporting detail for every collected signal. Evidence remains visible beside the score rather than being hidden inside the model.

### Decision output

GreySignal produces:

- final score from 0 (lowest modeled risk) to 100 (highest modeled risk);
- Low, Moderate, High, or Severe risk rating;
- proceed, proceed selectively, delay, or executive-acceptance recommendation;
- risk-factor table and visualization;
- supporting evidence and raw JSON response.

### Advanced intelligence output

- five domain-specialist findings with confidence values;
- BM25-ranked evidence retrieval and 64-dimensional local hash embeddings;
- keyword-based event extraction and rule-based sentiment;
- Prophet GDP-growth and inflation directional forecasts;
- predictions from XGBoost, CatBoost, and LightGBM;
- CatBoost SHAP feature contributions;
- MAPIE split-conformal 90% interval;
- NetworkX knowledge graph with nodes, edges, and centrality;
- optional Groq/Llama executive brief.

### Local assessment history

Every successful assessment is stored in `data/greysignal.sqlite`, including the country, sector, score, rating, timestamp, and complete response payload.

## How GreySignal Works

```text
User inputs (Streamlit wizard)
              |
              v
       POST /assess (FastAPI)
              |
              v
       LangGraph workflow
   initialize -> assess -> validate -> finalize
              |
              v
  Public evidence collection + business context
              |
              v
 Rule factors + ML ensemble + intelligence layers
              |
              v
 Recommendation, explanations, uncertainty, graph
              |
       +------+------+
       |             |
       v             v
 Streamlit result   SQLite history
```

LangGraph currently provides a deterministic four-node orchestration flow. The domain "agents" are structured specialist outputs generated from the evidence and factor results; they are not independent autonomous processes.

## Risk Methodology

### 1. Interpretable factor scores

Seven rule-based factors are calculated on a 0-100 risk scale:

| Factor | Weight | Primary input |
|---|---:|---|
| Macroeconomic growth | 20% | World Bank GDP growth |
| Inflation pressure | 18% | World Bank consumer-price inflation |
| Political stability | 22% | World Bank WGI political stability score |
| Weather disruption | 10% | Open-Meteo seven-day forecast |
| News and event risk | 18% | GDELT recent headlines and risk terms |
| Trade exposure | 12% | UN Comtrade availability/import context |
| Business fit | 10% | User-provided operating context |

These weights describe the interpretable rule-score layer. Business fit starts from a balanced baseline and is adjusted for investment size, entry mode, supply-chain and labor exposure, regulatory sensitivity, risk tolerance, local-partner availability, and time horizon.

Unavailable GDP, inflation, governance, or news observations generally receive a neutral factor score of 55. This keeps an external service failure from automatically becoming either a favorable or catastrophic signal.

### 2. Machine-learning ensemble

The backend trains three regressors at assessment time using `data/real_training_dataset.csv`:

- XGBoost Regressor;
- CatBoost Regressor;
- LightGBM Regressor.

Their predictions are averaged into an ensemble score.

### 3. Final displayed score

The final risk score shown to the user is:

```text
final score = (ML ensemble x 0.85) + (business-fit factor x 0.15)
```

The other rule-based factors remain important explanatory outputs, while their underlying indicators also contribute to the ML feature vector where available.

### 4. Rating and recommendation thresholds

| Score | Rating | Recommendation |
|---:|---|---|
| Below 35 | Low risk | Proceed with normal due diligence |
| 35 to below 60 | Moderate risk | Proceed selectively with controls and local validation |
| 60 to below 78 | High risk | Delay large commitments until key risks are mitigated |
| 78 to 100 | Severe risk | Do not proceed without executive-level risk acceptance |

## Data Sources

| Source | Data used | Credentials | Failure behavior |
|---|---|---|---|
| World Bank WDI API | GDP growth, inflation, unemployment, FDI, population | None | Marks signal unavailable |
| World Bank WGI bulk CSV | Political stability, government effectiveness, regulatory quality, rule of law, control of corruption | None | Uses local extracted data or attempts download |
| ExchangeRate-API | Current base/target exchange rate | API key required | Marks exchange rate unavailable |
| Open-Meteo | Seven-day temperature, rainfall, and wind forecast | None | Marks weather unavailable |
| GDELT DOC 2.0 | Recent relevant news headlines and optional historical event counts | None | Uses cached country news when possible |
| UN Comtrade | Import/trade value by reporter and HS code | API key required | Returns partial/unavailable trade evidence |
| User input | Investment and operating context | None | Included in business-fit factor |

The `.env.example` file contains the expected service URLs. `WORLD_BANK_DOCS_URL`, `OPEN_METEO_GEOCODING_URL`, and `ACLED_API_URL` are configurable placeholders but are not currently called by the assessment workflow.

## Machine Learning and Intelligence Layers

### Training features

The real country-year dataset supports these features:

- GDP growth;
- inflation;
- unemployment;
- foreign direct investment as a percentage of GDP;
- population;
- political stability;
- government effectiveness;
- regulatory quality;
- rule of law;
- control of corruption;
- optional GDELT risk-event count;
- optional UN Comtrade import value.

The training target is currently derived as:

```text
final_risk_score = 100 - political_stability_score
```

This makes political stability the supervised target definition, while the wider macroeconomic and governance feature set is used to learn the prediction.

### Explainability

SHAP `TreeExplainer` is applied to the CatBoost model. The API returns a feature-to-contribution mapping so users can inspect which inputs moved that model's prediction.

### Uncertainty

MAPIE `SplitConformalRegressor` produces a 90% split-conformal interval. The current implementation calculates this interval using a median training-feature proxy, so it should be interpreted as a model-level uncertainty indicator, not a fully individualized probability guarantee.

### Forecasting

Prophet produces one-step directional forecasts for GDP growth and inflation. It constructs a short synthetic trend ending at the latest collected observation; forecasts are therefore directional supporting signals, not production-grade macroeconomic forecasts.

### Retrieval and embeddings

`rank-bm25` ranks collected evidence against a country/sector risk query. A deterministic SHA-256-based local hash embedding creates a 64-dimensional evidence index without sending evidence to a remote embedding service.

### Events and sentiment

Event extraction maps configured keywords such as strike, protest, election, tariff, sanction, conflict, storm, flood, port, and shipment to risk categories. Sentiment is a transparent positive/negative keyword count over the collected evidence.

### LLM summary

When `GROQ_API_KEY` is configured, GreySignal requests an executive brief from `llama-3.1-8b-instant` through Groq. The prompt asks for a decision view, top risks, mitigations, and evidence caveats. The core assessment still runs without this key.

## Technology Stack and Libraries

### Application stack

| Component | Technology | Purpose |
|---|---|---|
| Frontend | Streamlit 1.41.1 | Guided wizard and interactive result dashboard |
| Visualization | Plotly 5.24.1 | Risk gauge and factor chart |
| Backend | FastAPI 0.115.6 | REST API and request routing |
| API server | Uvicorn 0.34.0 | ASGI development server |
| Validation | Pydantic 2.12.5 | Typed request and response schemas |
| Workflow | LangGraph 1.2.8 | Deterministic assessment orchestration |
| Storage | Python SQLite | Local assessment persistence |

### Data, ML, and intelligence libraries

| Library | Version | Use |
|---|---:|---|
| Requests | 2.32.3 | External HTTP integrations |
| pandas | 2.2.3 | Dataset and table processing |
| NumPy | Transitive dependency | Numerical arrays and ensemble calculations |
| scikit-learn | 1.7.2 | Supporting ML ecosystem |
| XGBoost | 3.2.0 | Gradient-boosted risk regression |
| LightGBM | 4.6.0 | Gradient-boosted risk regression |
| CatBoost | 1.2.10 | Gradient-boosted risk regression and SHAP model |
| SHAP | 0.49.1 | Feature-attribution explanation |
| Prophet | 1.3.0 | GDP/inflation directional forecasting |
| MAPIE | 1.4.1 | Split-conformal uncertainty interval |
| rank-bm25 | 0.2.2 | Evidence retrieval |
| NetworkX | 3.4.2 | Knowledge graph and centrality |
| python-dotenv | 1.2.2 | Environment configuration |

## System Architecture

### Frontend

`frontend/app.py` provides the five-step wizard, calls the backend, and renders the score, recommendation, evidence, factor chart, AI brief, agent findings, retrieval results, event/sentiment output, forecasts, model details, graph preview, and raw JSON.

### API and schemas

`backend/main.py` exposes health, country-list, and assessment endpoints. `backend/schemas.py` defines the complete Pydantic request and response contract.

### Service layer

- `api_clients.py` integrates external public-data services and manages the GDELT cache.
- `countries.py` contains country codes, currency, capital, coordinates, and Comtrade reporter identifiers.
- `dataset_builder.py` creates and loads the real country-year training dataset.
- `risk_engine.py` collects evidence, scores factors, combines model and business-fit outputs, and assembles the response.
- `final_intelligence.py` implements retrieval, agents, event/sentiment analysis, forecasts, models, SHAP, MAPIE, embeddings, and the knowledge graph.
- `llm_summary.py` optionally creates the Groq executive brief.
- `langgraph_workflow.py` orchestrates and validates the assessment lifecycle.
- `storage.py` stores successful assessments in SQLite.

## Project Structure

```text
GreySignal-hackathon-2026-main/
|-- backend/
|   |-- main.py                  # FastAPI application and routes
|   |-- config.py                # Environment-backed settings
|   |-- schemas.py               # Pydantic API contracts
|   `-- services/
|       |-- api_clients.py       # External data connectors
|       |-- countries.py         # Supported-country metadata
|       |-- dataset_builder.py   # Training-data construction
|       |-- final_intelligence.py# ML and intelligence layers
|       |-- langgraph_workflow.py# Workflow orchestration
|       |-- llm_summary.py       # Optional Groq summary
|       |-- risk_engine.py       # Assessment and scoring logic
|       `-- storage.py           # SQLite persistence
|-- frontend/
|   `-- app.py                   # Streamlit interface
|-- scripts/
|   `-- build_training_dataset.py
|-- data/
|   |-- real_training_dataset.csv
|   |-- greysignal.sqlite
|   |-- WGI_CSV.zip
|   `-- wgi_csv/
|-- .env.example
|-- .python-version              # Python 3.12
|-- requirements.txt
|-- requirements-frontend.txt
|-- run_backend.ps1
|-- run_frontend.ps1
`-- README.md
```

Runtime-generated files may include `data/gdelt_news_cache.json`, SQLite history, logs, and CatBoost training information.

## Supported Countries

The built-in profile registry currently includes 28 countries:

Australia, Bangladesh, Brazil, Canada, China, France, Germany, India, Indonesia, Italy, Japan, Malaysia, Mexico, Netherlands, Pakistan, Philippines, Poland, Saudi Arabia, Singapore, South Africa, South Korea, Spain, Thailand, Turkey, United Arab Emirates, United Kingdom, United States, and Vietnam.

The `/countries` endpoint returns this list. Unknown country names can pass schema validation, but missing ISO codes, coordinates, and reporter metadata will cause several evidence sources to be marked unavailable; use a configured country for a complete assessment.

## Installation and Configuration

### Prerequisites

- Windows PowerShell for the included launcher scripts;
- Python 3.12 (declared in `.python-version`);
- internet access for live public-data collection;
- optional ExchangeRate-API, UN Comtrade, and Groq credentials.

### 1. Create a virtual environment

Run commands from the directory containing `requirements.txt`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run this once for the current terminal:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### 2. Install dependencies

For the complete application:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

`requirements-frontend.txt` contains only the dashboard dependencies and is useful only when the frontend is installed separately. The full local application needs `requirements.txt`.

### 3. Create the environment file

```powershell
Copy-Item .env.example .env
```

The provided defaults configure the public endpoint URLs. Replace placeholder keys as required:

```env
GREYSIGNAL_API_URL=http://127.0.0.1:8010
HTTP_TIMEOUT_SECONDS=30

EXCHANGE_RATE_API_KEY=your_exchange_rate_key_here
UN_COMTRADE_API_KEY=your_un_comtrade_key_here
GROQ_API_KEY=your_groq_key_here
```

Do not commit `.env` or real credentials. The application loads `.env` with override enabled, so its values take precedence over existing process variables of the same name.

### Credential behavior

- **No ExchangeRate-API key:** the currency evidence is marked unavailable; assessment continues.
- **No UN Comtrade key:** trade data is partial/unavailable; assessment continues.
- **No Groq key:** the AI brief is empty, but all deterministic and ML analysis still runs.
- **No keys at all:** the project remains usable with reduced evidence coverage because World Bank, WGI, Open-Meteo, and GDELT do not require project-specific keys.

## Running the Application

Open two PowerShell terminals in the project directory after installing dependencies.

### Terminal 1: backend

```powershell
.\run_backend.ps1
```

This starts FastAPI with auto-reload at:

```text
http://127.0.0.1:8010
```

Interactive FastAPI documentation is available at:

```text
http://127.0.0.1:8010/docs
```

### Terminal 2: frontend

```powershell
.\run_frontend.ps1
```

Open the Streamlit URL printed in the terminal, normally:

```text
http://localhost:8501
```

The scripts assume `.venv` exists in the project root. `run_frontend.ps1` explicitly points the dashboard to backend port `8010`.

### Manual launch

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8010
```

In another terminal:

```powershell
$env:GREYSIGNAL_API_URL = "http://127.0.0.1:8010"
.\.venv\Scripts\python.exe -m streamlit run frontend/app.py
```

## Using the Dashboard

1. **Market:** choose a configured country and enter the sector/decision and city or port.
2. **Investment:** select investment size, entry mode, time horizon, and risk tolerance.
3. **Exposure:** define labor intensity, supply-chain dependence, regulatory sensitivity, and local-partner availability.
4. **Data:** choose currencies, HS code, World Bank year range, and news keywords.
5. **Review:** confirm the inputs and select **Start assessment**.

The result page shows the headline score first, then factor and evidence tables. Detailed tabs expose the AI brief, agent findings, retrieval results, event/sentiment signals, forecasts, model output, SHAP values, confidence interval, and knowledge graph.

## API Reference

### Health check

```http
GET /health
```

Example response:

```json
{
  "status": "ok",
  "service": "greysignal-api"
}
```

### Supported countries

```http
GET /countries
```

Returns an alphabetically sorted JSON array of configured country names.

### Create an assessment

```http
POST /assess
Content-Type: application/json
```

Complete example body:

```json
{
  "country": "Vietnam",
  "sector": "Manufacturing expansion",
  "city_or_port": "Hai Phong",
  "investment_size": "Medium",
  "entry_mode": "Greenfield",
  "time_horizon": "12-24 months",
  "risk_tolerance": "Medium",
  "labor_intensity": "Medium",
  "supply_chain_dependence": "High",
  "regulatory_sensitivity": "Medium",
  "local_partner_available": false,
  "news_keywords": "strike OR protest OR election OR tariff OR supply chain",
  "base_currency": "USD",
  "target_currency": "VND",
  "hs_code": "TOTAL",
  "start_year": 2020,
  "end_year": 2026
}
```

Minimal body (schema defaults fill the remaining fields):

```json
{
  "country": "Vietnam"
}
```

Example PowerShell request:

```powershell
$body = @{
    country = "Vietnam"
    sector = "Manufacturing expansion"
    city_or_port = "Hai Phong"
    base_currency = "USD"
    target_currency = "VND"
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri "http://127.0.0.1:8010/assess" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
```

The response contains the score, rating, recommendation, summary, factors, evidence, AI summary, specialist outputs, workflow trace, retrieval results, events, sentiment, forecasts, model outputs, SHAP explanation, confidence interval, knowledge graph, and UTC generation timestamp.

## Training Dataset

The repository includes `data/real_training_dataset.csv`. At the time this README was prepared, it contained 280 country-year records covering 28 configured countries and years 2015-2024.

### Rebuild in fast mode

```powershell
.\.venv\Scripts\python.exe scripts\build_training_dataset.py --start-year 2020 --end-year 2025 --fast
```

Fast mode collects World Bank WDI indicators and joins the World Bank WGI bulk dataset. It skips the slower per-country/year GDELT and UN Comtrade requests.

### Rebuild with slower optional sources

```powershell
.\.venv\Scripts\python.exe scripts\build_training_dataset.py --start-year 2020 --end-year 2025
```

This also attempts GDELT event counts and UN Comtrade values. These sources may be slower, rate-limited, or incomplete, and Comtrade requires a key.

The generated file is written to:

```text
data/real_training_dataset.csv
```

The ML assessment requires this file and at least 12 usable rows. If it is missing or too small, the assessment raises an error instructing you to rebuild it.

## Reliability and Fallback Behavior

GreySignal isolates most external evidence failures so one unavailable source does not stop the full collection phase:

- missing endpoint configuration is returned as unavailable evidence;
- HTTP failures are captured in the evidence detail;
- missing country metadata produces unavailable evidence rather than fabricated values;
- live GDELT failures use `data/gdelt_news_cache.json` when a previous result exists;
- missing API keys degrade only their related evidence and optional LLM output;
- neutral risk values are used for several unavailable rule-factor inputs;
- every evidence item carries a status such as `ok`, `cached`, `partial`, or `unavailable`.

The ML dataset is a hard dependency. Model-training, SHAP, MAPIE, unexpected data-shape errors, or uncaught local I/O errors can still fail an assessment.

## Limitations

- GreySignal is an MVP and has not been calibrated as a regulated credit, insurance, sanctions, or investment-rating product.
- The supervised target is derived from political stability, so the model is more strongly anchored to governance risk than to realized business loss.
- Models are retrained on every assessment rather than loaded from versioned, prevalidated artifacts.
- The current confidence interval uses a median-feature proxy and is not tailored to the exact current-country feature vector.
- Prophet uses a constructed short trend from the latest value, not a complete historical time series.
- News sentiment and event extraction are keyword/rule based and can miss context, negation, language variation, or duplicate coverage.
- Hash embeddings are deterministic local feature vectors, not semantic embeddings from a pretrained language model.
- Weather represents a seven-day operational signal and should not be interpreted as long-term climate-risk analysis.
- Trade scoring is currently availability-oriented rather than a deep sector-specific dependency model.
- Exchange-rate evidence is collected but is not represented as a separate weighted factor in the current final score.
- CORS is configured permissively (`*`) for development and should be restricted before deployment.
- SQLite is appropriate for a local MVP, not a multi-user production deployment without additional controls.
- No authentication, authorization, automated test suite, container definition, or production deployment configuration is included.

## Troubleshooting

### Frontend says the assessment failed

Confirm the backend is running and check:

```text
http://127.0.0.1:8010/health
```

The expected response has `"status": "ok"`.

### Frontend and backend use different ports

The included scripts use port `8010`. If launching manually on another port, set `GREYSIGNAL_API_URL` to the same address before starting Streamlit.

### `Real training dataset is missing or too small`

Rebuild the dataset with the fast command in [Training Dataset](#training-dataset), then retry the assessment.

### Currency, trade, or AI summary is unavailable

Verify the corresponding key in `.env`. Placeholder values such as `your_groq_key_here` are not valid credentials.

### External requests time out

Increase the value in `.env`, for example:

```env
HTTP_TIMEOUT_SECONDS=60
```

GDELT and UN Comtrade may also be temporarily rate-limited; retry later or use fast dataset mode.

### PowerShell cannot run the launcher scripts

Use the process-scoped execution-policy command shown in [Installation and Configuration](#installation-and-configuration), or run the manual launch commands.

## Responsible Use

GreySignal should be used as a transparent screening and scenario-analysis tool. Users should:

- verify critical evidence against primary sources;
- review unavailable, cached, or partial signals before acting;
- treat the AI brief as a summary, not an independent source of truth;
- involve legal, compliance, tax, security, supply-chain, and local-market experts;
- document the business assumptions behind each assessment;
- reassess when major events, policies, or operating plans change.

---

GreySignal turns scattered public signals into a structured first view of market-entry risk while keeping the evidence, assumptions, model behavior, and uncertainty visible to the decision-maker.
