# GreySignal

GreySignal is a geopolitical business risk intelligence MVP. A user selects a target country and business decision, then the app collects public signals and returns a scored expansion-risk assessment with supporting evidence.

## Current MVP Stack

- Frontend: Streamlit, Plotly
- Backend: FastAPI, Pydantic
- Data connectors: World Bank, World Bank WGI, ExchangeRate-API, Open-Meteo, GDELT, UN Comtrade
- Workflow: deterministic workflow graph steps
- Agents: economic, political-risk, trade, weather, and news specialist agents
- LLM summary: Groq-hosted Llama summary when `GROQ_API_KEY` is configured
- Retrieval: `rank-bm25` plus hash-embedding evidence index
- NLP: keyword event extraction and rule-based sentiment signal
- Forecasting: `Prophet` macro-indicator forecast
- Risk engine: weighted scoring plus real `XGBoost`, `CatBoost`, and `LightGBM` ensemble output
- Explainability: real `SHAP` explanation over the CatBoost model
- Confidence: real `MAPIE` split-conformal interval
- Knowledge graph: `NetworkX` graph JSON with country, decision, risk factors, and evidence nodes
- Storage: local SQLite assessment history

## Project Structure

```text
GreySignal/
  backend/
    main.py
    schemas.py
    services/
      api_clients.py
      countries.py
      risk_engine.py
  frontend/
    app.py
  requirements.txt
  run_backend.ps1
  run_frontend.ps1
```

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Copy `.env.example` to `.env`, then add private API keys locally:

```powershell
Copy-Item .env.example .env
```

The MVP reads external API base URLs and keys from `.env`. Keep `.env` private.

## Build Training Dataset

Generate the real country-year training dataset:

```powershell
.\.venv\Scripts\python.exe scripts\build_training_dataset.py --start-year 2020 --end-year 2025 --fast
```

This writes:

```text
data/real_training_dataset.csv
```

The ML layer automatically trains XGBoost, CatBoost, LightGBM, SHAP, and MAPIE from this CSV when it exists. Run without `--fast` to also attempt slower GDELT and UN Comtrade feature collection.

## Run

Open two PowerShell terminals.

Terminal 1:

```powershell
.\run_backend.ps1
```

Terminal 2:

```powershell
.\run_frontend.ps1
```

Then open the Streamlit URL shown in the terminal, usually:

```text
http://localhost:8501
```

## API

Health check:

```text
GET /health
```

Create assessment:

```text
POST /assess
```

Example body:

```json
{
  "country": "Vietnam",
  "sector": "Manufacturing expansion",
  "base_currency": "USD",
  "target_currency": "VND",
  "hs_code": "TOTAL",
  "start_year": 2020,
  "end_year": 2026
}
```

## Notes

The app is built to survive temporary API failures. If an external API is unreachable, the backend marks that evidence item as unavailable and applies a neutral score for that factor.

ExchangeRate-API and UN Comtrade require keys in `.env`:

```env
EXCHANGE_RATE_API_KEY=your_exchange_rate_key_here
UN_COMTRADE_API_KEY=your_un_comtrade_key_here
```

If a required key is missing, the backend marks that evidence item as unavailable and continues the assessment with a neutral risk score.
