$ErrorActionPreference = "Stop"
$env:GREYSIGNAL_API_URL = "http://127.0.0.1:8010"
streamlit run frontend/app.py
