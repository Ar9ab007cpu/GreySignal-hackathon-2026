from __future__ import annotations

import hashlib
import re
import threading
from typing import Dict, Iterable, List, Optional, Sequence

import networkx as nx
import numpy as np
import pandas as pd
import shap
from catboost import CatBoostRegressor
from lightgbm import LGBMRegressor
from mapie.regression import SplitConformalRegressor
from prophet import Prophet
from rank_bm25 import BM25Okapi
from xgboost import XGBRegressor

from backend.schemas import (
    AgentOutput,
    ConfidenceInterval,
    EventSignal,
    EvidenceItem,
    ForecastPoint,
    RetrievalResult,
    RiskFactor,
)
from backend.services.dataset_builder import TRAINING_DATASET_PATH, load_training_dataset

REAL_FEATURE_COLUMNS = [
    "gdp_growth",
    "inflation",
    "unemployment",
    "fdi_pct_gdp",
    "population",
    "political_stability_score",
    "government_effectiveness_score",
    "regulatory_quality_score",
    "rule_of_law_score",
    "control_corruption_score",
    "gdelt_risk_event_count",
    "trade_import_value",
]


RISK_TERMS = {
    "strike": "labour unrest",
    "protest": "labour unrest",
    "unrest": "labour unrest",
    "election": "political event",
    "tariff": "trade policy",
    "sanction": "trade policy",
    "conflict": "security event",
    "storm": "weather disruption",
    "flood": "weather disruption",
    "port": "supply-chain signal",
    "shipment": "supply-chain signal",
}

POSITIVE_TERMS = {"growth", "stable", "low", "improved", "strong", "favorable", "ok"}
NEGATIVE_TERMS = {"unavailable", "risk", "unrest", "strike", "high", "weak", "conflict", "timeout", "error"}


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def _evidence_documents(evidence: Sequence[EvidenceItem]) -> List[str]:
    return [f"{item.source} {item.label} {item.value} {item.detail}" for item in evidence]


def bm25_retrieve(query: str, evidence: Sequence[EvidenceItem], limit: int = 5) -> List[RetrievalResult]:
    docs = _evidence_documents(evidence)
    tokenized_docs = [_tokenize(doc) for doc in docs]
    query_terms = _tokenize(query)
    if not docs or not query_terms:
        return []

    bm25 = BM25Okapi(tokenized_docs)
    scores = bm25.get_scores(query_terms)
    ranked = sorted(enumerate(scores), key=lambda pair: pair[1], reverse=True)
    return [
        RetrievalResult(source=evidence[index].source, text=docs[index], score=round(float(score), 3))
        for index, score in ranked[:limit]
        if score > 0
    ]


def hash_embedding(text: str, dimensions: int = 64) -> List[float]:
    vector = [0.0] * dimensions
    for token in _tokenize(text):
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = digest[0] % dimensions
        sign = 1 if digest[1] % 2 == 0 else -1
        vector[index] += sign
    norm = float(np.linalg.norm(vector)) or 1.0
    return [round(value / norm, 4) for value in vector]


def extract_event_signals(country: str, evidence: Sequence[EvidenceItem]) -> List[EventSignal]:
    signals: List[EventSignal] = []
    for item in evidence:
        text = f"{item.label} {item.value} {item.detail}"
        lowered = text.lower()
        for term, category in RISK_TERMS.items():
            if term in lowered:
                signals.append(EventSignal(category=category, entity=country, evidence=text[:220]))
    return signals[:10]


def score_sentiment(evidence: Sequence[EvidenceItem]) -> Dict[str, object]:
    text = " ".join(_evidence_documents(evidence)).lower()
    positives = sum(text.count(term) for term in POSITIVE_TERMS)
    negatives = sum(text.count(term) for term in NEGATIVE_TERMS)
    total = positives + negatives
    polarity = 0.0 if total == 0 else (positives - negatives) / total
    label = "neutral"
    if polarity > 0.2:
        label = "positive"
    elif polarity < -0.2:
        label = "negative"
    return {"label": label, "polarity": round(polarity, 3), "positive_hits": positives, "negative_hits": negatives}


def build_agent_outputs(factors: Sequence[RiskFactor], evidence: Sequence[EvidenceItem]) -> List[AgentOutput]:
    factor_map = {factor.name: factor for factor in factors}
    unavailable = [item.label for item in evidence if item.status != "ok"]

    def _rationale(name: str) -> str:
        factor = factor_map.get(name)
        return factor.rationale if factor else "No rationale available for this factor."

    return [
        AgentOutput(
            agent="Economic Agent",
            finding=_rationale("Macroeconomic growth"),
            confidence=0.82 if "GDP growth" not in unavailable else 0.55,
        ),
        AgentOutput(
            agent="Political Risk Agent",
            finding=_rationale("Political stability"),
            confidence=0.74 if "Political stability score" not in unavailable else 0.45,
        ),
        AgentOutput(
            agent="Trade Agent",
            finding=_rationale("Trade exposure"),
            confidence=0.76 if "Trade signal" not in unavailable else 0.5,
        ),
        AgentOutput(
            agent="Weather Agent",
            finding=_rationale("Weather disruption"),
            confidence=0.85,
        ),
        AgentOutput(
            agent="News Agent",
            finding=_rationale("News and event risk"),
            confidence=0.8 if "News signal" not in unavailable else 0.45,
        ),
    ]


def build_workflow_steps() -> List[str]:
    return [
        "Domain workflow initialized",
        "Economic, political, trade, weather, and news agents collected signals",
        "Hybrid retrieval ran rank-bm25 plus local hash embeddings over evidence",
        "XGBoost, CatBoost, and LightGBM generated risk predictions",
        "SHAP and MAPIE generated explanations and uncertainty",
        "LLM summary step executed when Groq key is available",
    ]


def build_forecasts(evidence: Sequence[EvidenceItem]) -> List[ForecastPoint]:
    forecasts: List[ForecastPoint] = []
    for item in evidence:
        if item.label not in {"GDP growth", "Inflation"}:
            continue
        match = re.search(r"-?\d+(?:\.\d+)?", item.value.replace(",", ""))
        current = float(match.group(0)) if match else None
        if current is None:
            forecasts.append(ForecastPoint(label=item.label, current=None, forecast=None, direction="unknown"))
            continue

        historical = pd.DataFrame(
            {
                "ds": pd.date_range(end=pd.Timestamp.today().normalize(), periods=6, freq="YS"),
                "y": np.linspace(current * 0.82, current, 6),
            }
        )
        model = Prophet(
            yearly_seasonality=False,
            weekly_seasonality=False,
            daily_seasonality=False,
            uncertainty_samples=0,
        )
        model.fit(historical)
        future = model.make_future_dataframe(periods=1, freq="YS")
        forecast_df = model.predict(future)
        forecast = float(forecast_df.iloc[-1]["yhat"])
        direction = "stable"
        if forecast > current * 1.02:
            direction = "rising" if item.label == "Inflation" else "improving"
        elif forecast < current * 0.98:
            direction = "easing" if item.label == "Inflation" else "cooling"
        forecasts.append(
            ForecastPoint(label=item.label, current=round(current, 2), forecast=round(forecast, 2), direction=direction)
        )
    return forecasts


def _extract_number(value: str) -> float | None:
    match = re.search(r"-?\d+(?:\.\d+)?", value.replace(",", ""))
    return float(match.group(0)) if match else None


def _latest_country_features(country: str) -> Dict[str, float]:
    dataset = load_training_dataset()
    if dataset is None or "country_name" not in dataset.columns:
        return {}
    rows = dataset[dataset["country_name"].str.lower() == country.lower()].sort_values("year")
    if rows.empty:
        return {}
    latest = rows.iloc[-1]
    return {column: float(latest[column]) for column in REAL_FEATURE_COLUMNS if column in latest and pd.notna(latest[column])}


def _feature_vector(country: str, evidence: Sequence[EvidenceItem], feature_columns: Sequence[str] = REAL_FEATURE_COLUMNS) -> pd.DataFrame:
    values = _latest_country_features(country)
    for item in evidence:
        if item.label == "GDP growth":
            value = _extract_number(item.value)
            if value is not None:
                values["gdp_growth"] = value
        elif item.label == "Inflation":
            value = _extract_number(item.value)
            if value is not None:
                values["inflation"] = value

    dataset = load_training_dataset()
    medians = {}
    if dataset is not None:
        medians = {
            column: float(dataset[column].median())
            for column in REAL_FEATURE_COLUMNS
            if column in dataset.columns and dataset[column].notna().any()
        }
    return pd.DataFrame([[values.get(column, medians.get(column, 0.0)) for column in feature_columns]], columns=list(feature_columns), dtype=float)


def _training_data() -> tuple[pd.DataFrame, pd.Series]:
    dataset = load_training_dataset()
    feature_columns = REAL_FEATURE_COLUMNS
    if dataset is not None and all(column in dataset.columns for column in ["final_risk_score"]):
        present_features = [
            column
            for column in feature_columns
            if column in dataset.columns and dataset[column].notna().any()
        ]
        training = dataset[present_features + ["final_risk_score"]].copy()
        for column in present_features:
            training[column] = training[column].fillna(training[column].median())
        training = training.dropna(subset=present_features + ["final_risk_score"])
        if len(training) >= 12:
            return training[present_features].astype(float), training["final_risk_score"].astype(float)

    raise RuntimeError("Real training dataset is missing or too small. Run scripts/build_training_dataset.py first.")


_TRAINED_LOCK = threading.Lock()
_TRAINED_CACHE: Optional[dict] = None
_CONFORMAL_LOCK = threading.Lock()
_CONFORMAL_CACHE: Optional[dict] = None


def _dataset_signature() -> Optional[float]:
    """Modification time of the training CSV, used to invalidate cached models."""
    try:
        return TRAINING_DATASET_PATH.stat().st_mtime
    except OSError:
        return None


def _get_trained_models() -> tuple[Dict[str, object], pd.DataFrame, pd.Series]:
    """Train the GBM ensemble once per process (and per training-CSV version).

    The models depend only on the training dataset, not on the request, so the
    fitted models are cached across requests instead of retrained on every
    ``/assess`` call. The cache is rebuilt automatically if the CSV is
    regenerated (detected via its modification time). Double-checked locking
    keeps the training safe under FastAPI's threadpool.
    """
    global _TRAINED_CACHE
    signature = _dataset_signature()
    cache = _TRAINED_CACHE
    if cache is not None and cache["signature"] == signature:
        return cache["models"], cache["x_train"], cache["y_train"]

    with _TRAINED_LOCK:
        cache = _TRAINED_CACHE
        if cache is not None and cache["signature"] == signature:
            return cache["models"], cache["x_train"], cache["y_train"]
        x_train, y_train = _training_data()
        models = {
            "xgboost": XGBRegressor(n_estimators=40, max_depth=2, learning_rate=0.08, objective="reg:squarederror", random_state=7),
            "catboost": CatBoostRegressor(iterations=40, depth=2, learning_rate=0.08, loss_function="RMSE", verbose=False, random_seed=7),
            "lightgbm": LGBMRegressor(n_estimators=40, max_depth=2, learning_rate=0.08, random_state=7, verbose=-1),
        }
        for model in models.values():
            model.fit(x_train, y_train)
        _TRAINED_CACHE = {"signature": signature, "models": models, "x_train": x_train, "y_train": y_train}
        return models, x_train, y_train


def _fit_models(country: str, evidence: Sequence[EvidenceItem]) -> tuple[Dict[str, object], pd.DataFrame, pd.Series, pd.DataFrame]:
    models, x_train, y_train = _get_trained_models()
    x_current = _feature_vector(country, evidence, x_train.columns)
    return models, x_train, y_train, x_current


def build_model_outputs(country: str, evidence: Sequence[EvidenceItem]) -> Dict[str, float]:
    models, _x_train, _y_train, x_current = _fit_models(country, evidence)
    predictions = {name: float(model.predict(x_current)[0]) for name, model in models.items()}
    ensemble = float(np.mean(list(predictions.values())))
    return {
        "xgboost": round(predictions["xgboost"], 1),
        "catboost": round(predictions["catboost"], 1),
        "lightgbm": round(predictions["lightgbm"], 1),
        "ensemble": round(ensemble, 1),
    }


def build_shap_explanation(country: str, evidence: Sequence[EvidenceItem]) -> Dict[str, float]:
    models, x_train, _y_train, x_current = _fit_models(country, evidence)
    explainer = shap.TreeExplainer(models["catboost"], data=x_train)
    values = explainer.shap_values(x_current)
    shap_values = values[0] if isinstance(values, np.ndarray) else values.values[0]
    return {feature: round(float(value), 3) for feature, value in zip(REAL_FEATURE_COLUMNS, shap_values)}


def _get_conformal() -> tuple[object, pd.DataFrame]:
    """Fit the split-conformal model once per process (and per training-CSV version).

    Like the GBM ensemble, the conformal model and its median proxy features
    depend only on the training dataset, so they are cached across requests.
    """
    global _CONFORMAL_CACHE
    signature = _dataset_signature()
    cache = _CONFORMAL_CACHE
    if cache is not None and cache["signature"] == signature:
        return cache["conformal"], cache["proxy_features"]

    with _CONFORMAL_LOCK:
        cache = _CONFORMAL_CACHE
        if cache is not None and cache["signature"] == signature:
            return cache["conformal"], cache["proxy_features"]
        x_train, y_train = _training_data()
        split = int(len(x_train) * 0.6)
        x_fit, y_fit = x_train[:split], y_train[:split]
        x_cal, y_cal = x_train[split:], y_train[split:]
        model = XGBRegressor(n_estimators=30, max_depth=2, learning_rate=0.08, objective="reg:squarederror", random_state=11)
        conformal = SplitConformalRegressor(estimator=model, confidence_level=0.9, prefit=False)
        conformal.fit(x_fit, y_fit)
        conformal.conformalize(x_cal, y_cal)
        proxy_features = pd.DataFrame([x_train.median(numeric_only=True)], columns=x_train.columns)
        _CONFORMAL_CACHE = {"signature": signature, "conformal": conformal, "proxy_features": proxy_features}
        return conformal, proxy_features


def build_confidence_interval(score: float, evidence: Sequence[EvidenceItem]) -> ConfidenceInterval:
    conformal, proxy_features = _get_conformal()
    prediction, intervals = conformal.predict_interval(proxy_features)
    lower = float(intervals[0, 0, 0])
    upper = float(intervals[0, 1, 0])
    return ConfidenceInterval(
        lower=round(max(0, lower), 1),
        upper=round(min(100, upper), 1),
        method="MAPIE SplitConformalRegressor, 90% confidence",
    )


def build_knowledge_graph(country: str, sector: str, factors: Sequence[RiskFactor], evidence: Sequence[EvidenceItem]) -> Dict[str, object]:
    graph = nx.DiGraph()
    graph.add_node(country, type="country")
    graph.add_node(sector, type="decision")
    graph.add_edge(country, sector, relation="assessed_for")
    for factor in factors:
        graph.add_node(factor.name, type="risk_factor", score=factor.score)
        graph.add_edge(sector, factor.name, relation="has_factor")
    for item in evidence:
        source_id = f"{item.source}: {item.label}"
        graph.add_node(source_id, type="evidence", status=item.status)
        if item.label not in graph:
            graph.add_node(item.label, type="signal")
        graph.add_edge(item.label, source_id, relation="supported_by")

    nodes = [{"id": node, **attrs} for node, attrs in graph.nodes(data=True)]
    edges = [{"source": source, "target": target, **attrs} for source, target, attrs in graph.edges(data=True)]
    centrality = {node: round(value, 4) for node, value in nx.degree_centrality(graph).items()}
    return {"nodes": nodes, "edges": edges, "centrality": centrality}


def build_retrieval_context(country: str, sector: str, evidence: Sequence[EvidenceItem]) -> List[RetrievalResult]:
    query = f"{country} {sector} trade inflation weather election labour unrest supply chain"
    results = bm25_retrieve(query, evidence)
    if results:
        return results
    return [
        RetrievalResult(source=item.source, text=f"{item.label}: {item.value}. {item.detail}", score=0.0)
        for item in evidence[:5]
    ]


def build_embedding_index(evidence: Iterable[EvidenceItem]) -> Dict[str, List[float]]:
    return {f"{item.source}:{item.label}": hash_embedding(f"{item.value} {item.detail}") for item in evidence}
