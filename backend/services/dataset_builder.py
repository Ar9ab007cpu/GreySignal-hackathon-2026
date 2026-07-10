from __future__ import annotations

import time
import zipfile
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import numpy as np
import pandas as pd
import requests

from backend.config import settings
from backend.services.countries import COUNTRY_PROFILES

TRAINING_DATASET_PATH = Path("data/real_training_dataset.csv")
WGI_ZIP_PATH = Path("data/WGI_CSV.zip")
WGI_DIR = Path("data/wgi_csv")
WGI_CSV_PATH = WGI_DIR / "WGICSV.csv"
WGI_DOWNLOAD_URL = "https://databank.worldbank.org/data/download/WGI_CSV.zip"

WDI_INDICATORS = {
    "gdp_growth": "NY.GDP.MKTP.KD.ZG",
    "inflation": "FP.CPI.TOTL.ZG",
    "unemployment": "SL.UEM.TOTL.ZS",
    "fdi_pct_gdp": "BX.KLT.DINV.WD.GD.ZS",
    "population": "SP.POP.TOTL",
}

WGI_INDICATORS = {
    "political_stability_score": "GOV_WGI_PV.SC",
    "government_effectiveness_score": "GOV_WGI_GE.SC",
    "regulatory_quality_score": "GOV_WGI_RQ.SC",
    "rule_of_law_score": "GOV_WGI_RL.SC",
    "control_corruption_score": "GOV_WGI_CC.SC",
}


def _safe_get_json(url: str, params: Optional[Dict[str, Any]] = None) -> Any:
    response = requests.get(url, params=params, timeout=settings.http_timeout_seconds)
    response.raise_for_status()
    return response.json()


def _clip(value: float, low: float = 0, high: float = 100) -> float:
    return float(max(low, min(high, value)))


def _fetch_wdi_country_years(iso3: str, start_year: int, end_year: int) -> pd.DataFrame:
    rows: Dict[tuple[str, int], Dict[str, Any]] = {}
    if not settings.world_bank_base_url:
        return pd.DataFrame()

    for feature_name, indicator in WDI_INDICATORS.items():
        url = f"{settings.world_bank_base_url.rstrip('/')}/country/{iso3}/indicator/{indicator}"
        params = {"format": "json", "date": f"{start_year}:{end_year}", "per_page": 100}
        try:
            payload = _safe_get_json(url, params=params)
        except requests.RequestException:
            continue

        records = payload[1] if isinstance(payload, list) and len(payload) > 1 else []
        for item in records:
            year = item.get("date")
            value = item.get("value")
            if year is None:
                continue
            key = (iso3, int(year))
            rows.setdefault(key, {"country_iso3": iso3, "year": int(year)})
            rows[key][feature_name] = value

    return pd.DataFrame(rows.values())


def _fetch_wdi_batch(iso3_codes: List[str], start_year: int, end_year: int) -> pd.DataFrame:
    rows: Dict[tuple[str, int], Dict[str, Any]] = {}
    if not settings.world_bank_base_url or not iso3_codes:
        return pd.DataFrame()

    country_path = ";".join(iso3_codes)
    for feature_name, indicator in WDI_INDICATORS.items():
        url = f"{settings.world_bank_base_url.rstrip('/')}/country/{country_path}/indicator/{indicator}"
        params = {"format": "json", "date": f"{start_year}:{end_year}", "per_page": 20000}
        try:
            payload = _safe_get_json(url, params=params)
        except requests.RequestException:
            continue

        records = payload[1] if isinstance(payload, list) and len(payload) > 1 else []
        for item in records:
            country = item.get("countryiso3code")
            year = item.get("date")
            value = item.get("value")
            if not country or year is None:
                continue
            key = (country, int(year))
            rows.setdefault(key, {"country_iso3": country, "year": int(year)})
            rows[key][feature_name] = value

    return pd.DataFrame(rows.values())


def _ensure_wgi_csv() -> None:
    WGI_DIR.mkdir(parents=True, exist_ok=True)
    if WGI_CSV_PATH.exists():
        return
    WGI_ZIP_PATH.parent.mkdir(parents=True, exist_ok=True)
    response = requests.get(WGI_DOWNLOAD_URL, timeout=settings.http_timeout_seconds)
    response.raise_for_status()
    WGI_ZIP_PATH.write_bytes(response.content)
    with zipfile.ZipFile(WGI_ZIP_PATH) as archive:
        archive.extractall(WGI_DIR)


def _load_wgi_scores(start_year: int, end_year: int) -> pd.DataFrame:
    _ensure_wgi_csv()
    raw = pd.read_csv(WGI_CSV_PATH)
    raw = raw[raw["Indicator Code"].isin(WGI_INDICATORS.values())]
    year_columns = [str(year) for year in range(start_year, end_year + 1) if str(year) in raw.columns]
    melted = raw.melt(
        id_vars=["Country Name", "Country Code", "Indicator Code"],
        value_vars=year_columns,
        var_name="year",
        value_name="value",
    )
    melted["year"] = melted["year"].astype(int)
    code_to_feature = {code: feature for feature, code in WGI_INDICATORS.items()}
    melted["feature"] = melted["Indicator Code"].map(code_to_feature)
    wide = (
        melted.pivot_table(index=["Country Code", "year"], columns="feature", values="value", aggfunc="first")
        .reset_index()
        .rename(columns={"Country Code": "country_iso3"})
    )
    return wide


def _fetch_gdelt_count(country_name: str, year: int) -> Optional[int]:
    if not settings.gdelt_doc_url:
        return None
    query = f'"{country_name}" (strike OR protest OR election OR tariff OR sanction OR unrest)'
    params = {
        "query": query,
        "mode": "timelinevolraw",
        "format": "json",
        "startdatetime": f"{year}0101000000",
        "enddatetime": f"{year}1231235959",
    }
    try:
        payload = _safe_get_json(settings.gdelt_doc_url, params=params)
    except requests.RequestException:
        return None

    timeline = payload.get("timeline", []) if isinstance(payload, dict) else []
    if not timeline:
        return None
    return int(sum(point.get("value", 0) for point in timeline if isinstance(point, dict)))


def _fetch_comtrade_value(reporter_code: str, year: int, hs_code: str = "TOTAL") -> Optional[float]:
    if not settings.un_comtrade_url or not settings.un_comtrade_api_key:
        return None

    params = {
        "cmdCode": hs_code,
        "flowCode": "M",
        "reporterCode": reporter_code,
        "partnerCode": "0",
        "period": year,
        "includeDesc": "true",
        "subscription-key": settings.un_comtrade_api_key,
    }
    try:
        payload = _safe_get_json(settings.un_comtrade_url, params=params)
    except requests.RequestException:
        return None

    records = payload.get("data", []) if isinstance(payload, dict) else []
    total = 0.0
    for record in records:
        for key in ("primaryValue", "cifvalue", "fobvalue", "netWgt"):
            value = record.get(key)
            if isinstance(value, (int, float)):
                total += float(value)
                break
    return total if total > 0 else None


def _build_target_scores(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["final_risk_score"] = (100 - df["political_stability_score"]).round(2)
    df["risk_label"] = pd.cut(
        df["final_risk_score"],
        bins=[-1, 35, 60, 78, 101],
        labels=["Low risk", "Moderate risk", "High risk", "Severe risk"],
    ).astype(str)
    return df


def build_training_dataset(
    countries: Optional[Iterable[str]] = None,
    start_year: int = 2020,
    end_year: int = 2025,
    hs_code: str = "TOTAL",
    include_slow_sources: bool = True,
) -> pd.DataFrame:
    selected = list(countries or COUNTRY_PROFILES.keys())
    frames: List[pd.DataFrame] = []
    wgi_scores = _load_wgi_scores(start_year, end_year)
    selected_profiles = {country_key: COUNTRY_PROFILES[country_key] for country_key in selected}
    wdi_batch = _fetch_wdi_batch([profile["iso3"] for profile in selected_profiles.values()], start_year, end_year)

    for country_key, profile in selected_profiles.items():
        frame = wdi_batch[wdi_batch["country_iso3"] == profile["iso3"]].copy()
        if frame.empty:
            continue
        frame = frame.merge(wgi_scores, on=["country_iso3", "year"], how="left")
        frame["country_name"] = country_key.title()
        frame["country_iso2"] = profile["iso2"]
        frame["currency"] = profile["currency"]
        frame["gdelt_risk_event_count"] = np.nan
        frame["trade_import_value"] = np.nan

        if include_slow_sources:
            for index, row in frame.iterrows():
                year = int(row["year"])
                frame.at[index, "gdelt_risk_event_count"] = _fetch_gdelt_count(country_key.title(), year)
                time.sleep(0.4)
                frame.at[index, "trade_import_value"] = _fetch_comtrade_value(
                    profile["comtrade_reporter_code"],
                    year,
                    hs_code,
                )
                time.sleep(0.2)

        frames.append(frame)

    if not frames:
        raise RuntimeError("No training rows could be built from the configured data sources.")

    dataset = pd.concat(frames, ignore_index=True)
    dataset = dataset.dropna(subset=["political_stability_score"])
    dataset = _build_target_scores(dataset)
    dataset = dataset.sort_values(["country_iso3", "year"]).reset_index(drop=True)
    TRAINING_DATASET_PATH.parent.mkdir(parents=True, exist_ok=True)
    dataset.to_csv(TRAINING_DATASET_PATH, index=False)
    return dataset


def load_training_dataset() -> Optional[pd.DataFrame]:
    if not TRAINING_DATASET_PATH.exists():
        return None
    return pd.read_csv(TRAINING_DATASET_PATH)
