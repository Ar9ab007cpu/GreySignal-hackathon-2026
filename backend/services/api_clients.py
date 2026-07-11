from __future__ import annotations

import json
import time
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

from backend.config import settings
from backend.schemas import EvidenceItem
from backend.services.dataset_builder import WGI_INDICATORS, _load_wgi_scores

GDELT_CACHE_PATH = Path("data/gdelt_news_cache.json")

def _get_json(url: str, params: Optional[Dict[str, Any]] = None, max_retries: int = 3) -> Any:
    """HTTP GET with exponential backoff for 429 rate-limit responses."""
    last_exc: Optional[Exception] = None
    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, timeout=settings.http_timeout_seconds)
            if response.status_code == 429 and attempt < max_retries - 1:
                wait = 2 ** (attempt + 1)           # 2s, 4s, 8s
                time.sleep(wait)
                continue
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            last_exc = exc
            if "429" in str(exc) and attempt < max_retries - 1:
                time.sleep(2 ** (attempt + 1))
                continue
            raise
    raise last_exc  # type: ignore[misc]


def _unavailable(source: str, label: str, detail: str) -> EvidenceItem:
    return EvidenceItem(
        source=source,
        label=label,
        value="Unavailable",
        status="unavailable",
        detail=detail,
    )


def fetch_world_bank_indicator(
    iso3: str,
    indicator: str,
    label: str,
    start_year: int,
    end_year: int,
    source: str = "World Bank",
) -> EvidenceItem:
    if not iso3:
        return _unavailable(source, label, "Country ISO3 code is not configured.")
    if not settings.world_bank_base_url:
        return _unavailable(source, label, "WORLD_BANK_BASE_URL is not configured.")

    url = f"{settings.world_bank_base_url.rstrip('/')}/country/{iso3}/indicator/{indicator}"
    params = {"format": "json", "date": f"{start_year}:{end_year}", "per_page": 10}

    try:
        payload = _get_json(url, params=params)
        if isinstance(payload, list) and payload and isinstance(payload[0], dict) and "message" in payload[0]:
            messages = payload[0].get("message", [])
            detail = "; ".join(message.get("value", "") for message in messages if isinstance(message, dict))
            return _unavailable(source, label, detail or "World Bank returned an indicator error.")

        rows = payload[1] if isinstance(payload, list) and len(payload) > 1 else []
        row = next((item for item in rows if item.get("value") is not None), None)
        if not row:
            return _unavailable(source, label, "No recent value returned by World Bank.")

        value = row["value"]
        year = row.get("date", "latest")
        if isinstance(value, (int, float)):
            formatted = f"{value:,.2f}"
        else:
            formatted = str(value)

        return EvidenceItem(
            source=source,
            label=label,
            value=f"{formatted} ({year})",
            detail=f"Indicator {indicator}",
        )
    except requests.RequestException as exc:
        return _unavailable(source, label, str(exc))


def fetch_wgi_political_stability(iso3: str, start_year: int, end_year: int) -> EvidenceItem:
    if not iso3:
        return _unavailable("World Bank WGI", "Political stability score", "Country ISO3 code is not configured.")

    try:
        wgi = _load_wgi_scores(start_year, end_year)
    except (requests.RequestException, OSError, ValueError) as exc:
        return _unavailable("World Bank WGI", "Political stability score", str(exc))

    rows = wgi[(wgi["country_iso3"] == iso3) & wgi["political_stability_score"].notna()].sort_values("year")
    if rows.empty:
        return _unavailable("World Bank WGI", "Political stability score", "No WGI political stability score found.")

    latest = rows.iloc[-1]
    value = float(latest["political_stability_score"])
    year = int(latest["year"])
    return EvidenceItem(
        source="World Bank WGI",
        label="Political stability score",
        value=f"{value:.2f} ({year})",
        detail=f"Indicator {WGI_INDICATORS['political_stability_score']}; governance score 0-100",
    )


def fetch_exchange_rate(base: str, target: str) -> EvidenceItem:
    base = base.upper()
    target = target.upper()
    if not settings.exchange_rate_api_base_url:
        return _unavailable("ExchangeRate-API", "Exchange rate", "EXCHANGE_RATE_API_BASE_URL is not configured.")
    if not settings.exchange_rate_api_key:
        return _unavailable("ExchangeRate-API", "Exchange rate", "EXCHANGE_RATE_API_KEY is not configured.")

    url = f"{settings.exchange_rate_api_base_url.rstrip('/')}/{settings.exchange_rate_api_key}/latest/{base}"

    try:
        payload = _get_json(url)
        rate = payload.get("conversion_rates", {}).get(target)
        if rate is None:
            return _unavailable("ExchangeRate-API", "Exchange rate", f"No {base}/{target} rate.")

        return EvidenceItem(
            source="ExchangeRate-API",
            label="Exchange rate",
            value=f"1 {base} = {rate:,.4f} {target}",
            detail=f"Last update: {payload.get('time_last_update_utc', 'latest')}",
        )
    except requests.RequestException as exc:
        return _unavailable("ExchangeRate-API", "Exchange rate", str(exc))


def fetch_weather_risk(latitude: float, longitude: float) -> EvidenceItem:
    if not latitude and not longitude:
        return _unavailable("Open-Meteo", "Weather risk", "Coordinates are not configured.")
    if not settings.open_meteo_forecast_url:
        return _unavailable("Open-Meteo", "Weather risk", "OPEN_METEO_FORECAST_URL is not configured.")

    today = date.today()
    url = settings.open_meteo_forecast_url
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max,precipitation_sum,wind_speed_10m_max",
        "timezone": "auto",
        "start_date": today.isoformat(),
        "end_date": (today + timedelta(days=6)).isoformat(),
    }

    try:
        payload = _get_json(url, params=params)
        daily = payload.get("daily", {})
        max_temp = max(daily.get("temperature_2m_max", [0]))
        max_precip = max(daily.get("precipitation_sum", [0]))
        max_wind = max(daily.get("wind_speed_10m_max", [0]))
        flags = []
        if max_temp >= 38:
            flags.append("extreme heat")
        if max_precip >= 50:
            flags.append("heavy rainfall")
        if max_wind >= 60:
            flags.append("high wind")

        value = "Low near-term weather disruption"
        if flags:
            value = "Potential disruption: " + ", ".join(flags)

        return EvidenceItem(
            source="Open-Meteo",
            label="7-day weather risk",
            value=value,
            detail=f"Max temp {max_temp:.1f} C, max rain {max_precip:.1f} mm, max wind {max_wind:.1f} km/h",
        )
    except (requests.RequestException, ValueError) as exc:
        return _unavailable("Open-Meteo", "Weather risk", str(exc))


def _fetch_mediastack_news(country: str, keywords: str = "") -> Optional[EvidenceItem]:
    """Primary news source using MediaStack API.

    MediaStack treats a multi-term ``keywords`` string as AND/phrase rather than
    boolean OR, so passing the GDELT-style risk-term list returns zero results
    for most countries. We therefore query on the country name alone (which
    reliably returns recent coverage) and let downstream news scoring scan the
    returned headlines for risk terms. ``keywords`` is accepted for API
    compatibility but intentionally not sent to MediaStack.
    """
    if not settings.mediastack_api_url or not settings.mediastack_api_key:
        return None

    params = {
        "access_key": settings.mediastack_api_key,
        "keywords": country,
        "languages": "en",
        "limit": 5,
        "sort": "published_desc",
    }

    try:
        payload = _get_json(settings.mediastack_api_url, params=params, max_retries=2)
        articles: List[Dict[str, Any]] = payload.get("data", [])
        if not articles:
            return None

        titles = [article.get("title", "Untitled") for article in articles[:3]]
        return EvidenceItem(
            source="MediaStack",
            label="News signal",
            value=f"{len(articles)} relevant recent articles",
            detail=" | ".join(titles),
        )
    except requests.RequestException:
        return None


def fetch_gdelt_news(country: str, keywords: str = "business OR trade OR election OR unrest") -> EvidenceItem:
    # MediaStack is the primary news source. GDELT's public endpoint frequently
    # returns HTTP 429, so it is only used as a fallback when MediaStack is
    # unavailable or returns no data.
    ms = _fetch_mediastack_news(country, keywords)
    if ms:
        _write_gdelt_cache(country, ms)
        return ms

    if not settings.gdelt_doc_url:
        cached = _read_gdelt_cache(country)
        if cached:
            cached.status = "cached"
            return cached
        return _unavailable(
            "News signal",
            "News signal",
            "MediaStack returned no data and GDELT_DOC_URL is not configured.",
        )

    url = settings.gdelt_doc_url
    params = {
        "query": f'"{country}" ({keywords})',
        "mode": "ArtList",
        "format": "json",
        "maxrecords": 5,
        "sort": "HybridRel",
    }

    try:
        payload = _get_json(url, params=params)
        articles: List[Dict[str, Any]] = payload.get("articles", [])
        if not articles:
            cached = _read_gdelt_cache(country)
            if cached:
                cached.status = "cached"
                return cached
            return _unavailable("GDELT", "News signal", "No articles returned.")

        titles = [article.get("title", "Untitled") for article in articles[:3]]
        item = EvidenceItem(
            source="GDELT",
            label="News signal",
            value=f"{len(articles)} relevant recent articles",
            detail=" | ".join(titles),
        )
        _write_gdelt_cache(country, item)
        return item
    except requests.RequestException as exc:
        # GDELT failed (likely 429) — fall back to the last cached signal.
        cached = _read_gdelt_cache(country)
        if cached:
            cached.status = "cached"
            cached.detail = f"{cached.detail} | Live GDELT unavailable: {exc}"
            return cached
        return _unavailable("GDELT", "News signal", f"Live GDELT unavailable: {exc}")


def _read_gdelt_cache(country: str) -> Optional[EvidenceItem]:
    if not GDELT_CACHE_PATH.exists():
        return None
    try:
        data = json.loads(GDELT_CACHE_PATH.read_text(encoding="utf-8"))
        item = data.get(country.lower())
        return EvidenceItem(**item) if item else None
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return None


def _write_gdelt_cache(country: str, item: EvidenceItem) -> None:
    GDELT_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        data = json.loads(GDELT_CACHE_PATH.read_text(encoding="utf-8")) if GDELT_CACHE_PATH.exists() else {}
    except (OSError, json.JSONDecodeError):
        data = {}
    data[country.lower()] = item.model_dump()
    GDELT_CACHE_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def fetch_trade_signal(reporter_code: str, hs_code: str = "TOTAL") -> EvidenceItem:
    if not reporter_code:
        return _unavailable("UN Comtrade", "Trade signal", "Country reporter code is not configured.")
    if not settings.un_comtrade_url:
        return _unavailable("UN Comtrade", "Trade signal", "UN_COMTRADE_URL is not configured.")
    if not settings.un_comtrade_api_key:
        return _unavailable("UN Comtrade", "Trade signal", "UN_COMTRADE_API_KEY is not configured.")

    params = {
        "cmdCode": hs_code or "TOTAL",
        "flowCode": "M",
        "reporterCode": reporter_code,
        "partnerCode": "0",
        "period": date.today().year - 1,
        "includeDesc": "true",
        "subscription-key": settings.un_comtrade_api_key,
    }

    try:
        payload = _get_json(settings.un_comtrade_url, params=params)
        rows = payload.get("data", []) if isinstance(payload, dict) else []
        return EvidenceItem(
            source="UN Comtrade",
            label="Trade signal",
            value=f"{len(rows)} trade records returned",
            detail=f"Reporter {reporter_code}, HS {params['cmdCode']}, year {params['period']}",
        )
    except requests.RequestException as exc:
        return _unavailable("UN Comtrade", "Trade signal", str(exc))
