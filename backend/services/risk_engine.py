from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Callable, List, Tuple, TypeVar

from backend.schemas import AssessmentRequest, AssessmentResponse, EvidenceItem, RiskFactor
from backend.services.api_clients import (
    fetch_exchange_rate,
    fetch_gdelt_news,
    fetch_trade_signal,
    fetch_weather_risk,
    fetch_wgi_political_stability,
    fetch_world_bank_indicator,
)
from backend.services.countries import get_country_profile
from backend.services.final_intelligence import (
    build_agent_outputs,
    build_confidence_interval,
    build_embedding_index,
    build_forecasts,
    build_knowledge_graph,
    build_model_outputs,
    build_retrieval_context,
    build_shap_explanation,
    build_workflow_steps,
    extract_event_signals,
    score_sentiment,
)
from backend.services.llm_summary import build_groq_summary
from backend.services.storage import save_assessment

logger = logging.getLogger("greysignal.risk_engine")

T = TypeVar("T")


def _safe(step: str, fn: Callable[[], T], default: T) -> T:
    """Run an analytics step, returning ``default`` if it fails.

    The intelligence/ML layer must never break a whole assessment: a failure in
    one enrichment step (model training, SHAP, forecasting, graph, storage, ...)
    is logged and degraded to a neutral default so the core risk result is still
    returned.
    """
    try:
        return fn()
    except Exception as exc:  # noqa: BLE001 - deliberately broad; analytics is best-effort
        logger.warning("GreySignal step '%s' failed: %s", step, exc)
        return default


def _safe_evidence(source: str, label: str, fn: Callable[[], EvidenceItem]) -> EvidenceItem:
    """Fetch one evidence item, degrading to an 'unavailable' item on any error."""
    try:
        return fn()
    except Exception as exc:  # noqa: BLE001 - a single connector must not break the request
        logger.warning("GreySignal evidence '%s' failed: %s", label, exc)
        return EvidenceItem(source=source, label=label, value="Unavailable", status="unavailable", detail=str(exc))


def _number_from_value(value: str) -> float | None:
    tokens = value.split()
    if not tokens:
        return None
    token = tokens[0].replace(",", "")
    try:
        return float(token)
    except ValueError:
        return None


def _score_gdp(gdp_growth: EvidenceItem) -> RiskFactor:
    value = _number_from_value(gdp_growth.value)
    if value is None:
        score = 55
        rationale = "GDP growth data is unavailable, so the model applies a neutral risk score."
    elif value >= 5:
        score = 25
        rationale = "Strong GDP growth lowers expansion risk."
    elif value >= 2:
        score = 45
        rationale = "Moderate GDP growth suggests manageable macroeconomic risk."
    elif value >= 0:
        score = 65
        rationale = "Low GDP growth raises demand and execution risk."
    else:
        score = 85
        rationale = "Negative GDP growth indicates elevated macroeconomic risk."

    return RiskFactor(name="Macroeconomic growth", score=score, weight=0.2, rationale=rationale)


def _score_inflation(inflation: EvidenceItem) -> RiskFactor:
    value = _number_from_value(inflation.value)
    if value is None:
        score = 55
        rationale = "Inflation data is unavailable, so the model applies a neutral risk score."
    elif value <= 4:
        score = 25
        rationale = "Inflation appears controlled, reducing pricing and wage pressure."
    elif value <= 8:
        score = 50
        rationale = "Inflation is material but not yet a severe business constraint."
    else:
        score = 80
        rationale = "High inflation increases cost, wage, and currency risk."

    return RiskFactor(name="Inflation pressure", score=score, weight=0.18, rationale=rationale)


def _score_governance(stability: EvidenceItem) -> RiskFactor:
    value = _number_from_value(stability.value)
    if value is None:
        score = 55
        rationale = "Political stability data is unavailable, so the model applies a neutral risk score."
    elif value >= 70:
        score = 25
        rationale = "Political stability is relatively favorable."
    elif value >= 45:
        score = 50
        rationale = "Political stability is mixed and requires monitoring."
    else:
        score = 80
        rationale = "Weak political stability increases policy and disruption risk."

    return RiskFactor(name="Political stability", score=score, weight=0.22, rationale=rationale)


def _score_weather(weather: EvidenceItem) -> RiskFactor:
    score = 30 if weather.status == "ok" and "Low" in weather.value else 65
    rationale = (
        "Near-term weather does not indicate major disruption."
        if score == 30
        else "Weather data suggests possible disruption or could not be verified."
    )
    return RiskFactor(name="Weather disruption", score=score, weight=0.1, rationale=rationale)


def _score_news(news: EvidenceItem) -> RiskFactor:
    risky_words = ["unrest", "strike", "conflict", "tariff", "sanction", "election"]
    detail = news.detail.lower()
    hits = sum(1 for word in risky_words if word in detail)
    if news.status != "ok":
        score = 55
        rationale = "News signal is unavailable, so the model applies a neutral risk score."
    elif hits >= 2:
        score = 70
        rationale = "Recent headlines include multiple risk terms that require analyst review."
    elif hits == 1:
        score = 50
        rationale = "Recent news contains one risk-related signal."
    else:
        score = 35
        rationale = "Recent news does not show strong immediate disruption signals."

    return RiskFactor(name="News and event risk", score=score, weight=0.18, rationale=rationale)


def _score_trade(trade: EvidenceItem) -> RiskFactor:
    if trade.status in {"ok", "cached"}:
        score = 45
        rationale = "Trade signal retrieved; deeper scoring can be enabled with fuller Comtrade history."
    else:
        score = 60
        rationale = "Trade signal could not be verified, so a mildly elevated neutral score is applied."
    return RiskFactor(name="Trade exposure", score=score, weight=0.12, rationale=rationale)


def _score_business_context(request: AssessmentRequest) -> RiskFactor:
    score = 35.0
    reasons = []

    if request.investment_size.lower() == "large":
        score += 12
        reasons.append("large investment increases downside exposure")
    elif request.investment_size.lower() == "small":
        score -= 5
        reasons.append("smaller investment limits exposure")

    if request.entry_mode.lower() in {"greenfield", "acquisition"}:
        score += 10
        reasons.append(f"{request.entry_mode.lower()} entry requires higher local execution commitment")
    elif request.entry_mode.lower() == "joint venture":
        score -= 4
        reasons.append("joint venture can reduce local execution risk")

    if request.supply_chain_dependence.lower() == "high":
        score += 10
        reasons.append("high supply-chain dependence increases disruption sensitivity")
    if request.labor_intensity.lower() == "high":
        score += 8
        reasons.append("high labor intensity increases exposure to wage and unrest risk")
    if request.regulatory_sensitivity.lower() == "high":
        score += 8
        reasons.append("high regulatory sensitivity increases policy risk")
    if request.risk_tolerance.lower() == "low":
        score += 8
        reasons.append("low risk tolerance raises the effective risk threshold")
    elif request.risk_tolerance.lower() == "high":
        score -= 5
        reasons.append("high risk tolerance lowers the effective risk threshold")
    if request.local_partner_available:
        score -= 8
        reasons.append("local partner availability reduces execution risk")
    if request.time_horizon.lower() in {"0-6 months", "6-12 months"}:
        score += 5
        reasons.append("short time horizon leaves less time to mitigate risks")

    score = max(0, min(100, score))
    rationale = "; ".join(reasons) if reasons else "Business context indicates a balanced risk profile."
    return RiskFactor(name="Business fit", score=score, weight=0.1, rationale=rationale)


def _rating(score: float) -> str:
    if score < 35:
        return "Low risk"
    if score < 60:
        return "Moderate risk"
    if score < 78:
        return "High risk"
    return "Severe risk"


def _recommendation(score: float) -> str:
    if score < 35:
        return "Proceed, with normal due diligence."
    if score < 60:
        return "Proceed selectively, with risk controls and local validation."
    if score < 78:
        return "Delay large commitments until key risks are mitigated."
    return "Do not proceed without executive-level risk acceptance."


def build_assessment(request: AssessmentRequest) -> AssessmentResponse:
    profile = get_country_profile(request.country)

    # Each connector is independent, so fetch all evidence concurrently. The
    # calls are network-bound; running them in parallel turns the slowest single
    # request (instead of the sum of all seven) into the wall-clock cost.
    evidence_tasks: List[Tuple[str, str, Callable[[], EvidenceItem]]] = [
        ("World Bank", "GDP growth", lambda: fetch_world_bank_indicator(
            profile["iso3"],
            "NY.GDP.MKTP.KD.ZG",
            "GDP growth",
            request.start_year,
            request.end_year,
        )),
        ("World Bank", "Inflation", lambda: fetch_world_bank_indicator(
            profile["iso3"],
            "FP.CPI.TOTL.ZG",
            "Inflation",
            request.start_year,
            request.end_year,
        )),
        ("World Bank WGI", "Political stability score", lambda: fetch_wgi_political_stability(
            profile["iso3"],
            request.start_year,
            request.end_year,
        )),
        ("ExchangeRate-API", "Exchange rate", lambda: fetch_exchange_rate(
            request.base_currency, request.target_currency or profile["currency"]
        )),
        ("Open-Meteo", "Weather risk", lambda: fetch_weather_risk(profile["lat"], profile["lon"])),
        ("GDELT", "News signal", lambda: fetch_gdelt_news(profile["name"], request.news_keywords)),
        ("UN Comtrade", "Trade signal", lambda: fetch_trade_signal(
            profile["comtrade_reporter_code"], request.hs_code
        )),
    ]
    with ThreadPoolExecutor(max_workers=len(evidence_tasks)) as executor:
        evidence: List[EvidenceItem] = list(
            executor.map(lambda task: _safe_evidence(*task), evidence_tasks)
        )

    factors = [
        _score_gdp(evidence[0]),
        _score_inflation(evidence[1]),
        _score_governance(evidence[2]),
        _score_weather(evidence[4]),
        _score_news(evidence[5]),
        _score_trade(evidence[6]),
        _score_business_context(request),
    ]
    overall = sum(factor.score * factor.weight for factor in factors)
    rating = _rating(overall)

    summary = (
        f"GreySignal assessed {profile['name']} for {request.sector}. "
        f"The current composite score is {overall:.1f}/100, classified as {rating.lower()}."
    )

    neutral_outputs = {
        "xgboost": round(overall, 1),
        "catboost": round(overall, 1),
        "lightgbm": round(overall, 1),
        "ensemble": round(overall, 1),
    }
    model_outputs = _safe("model_outputs", lambda: build_model_outputs(profile["name"], evidence), neutral_outputs)
    business_fit = next((factor for factor in factors if factor.name == "Business fit"), None)
    business_score = business_fit.score if business_fit else model_outputs["ensemble"]
    final_score = (model_outputs["ensemble"] * 0.85) + (business_score * 0.15)
    final_rating = _rating(final_score)
    final_recommendation = _recommendation(final_score)
    final_summary = (
        f"GreySignal assessed {profile['name']} for {request.sector}. "
        f"The final ensemble score is {final_score:.1f}/100, classified as {final_rating.lower()}."
    )

    response = AssessmentResponse(
        country=profile["name"],
        sector=request.sector,
        overall_score=round(final_score, 1),
        rating=final_rating,
        recommendation=final_recommendation,
        summary=final_summary,
        factors=factors,
        evidence=evidence,
        ai_summary=_safe("ai_summary", lambda: build_groq_summary(
            request,
            profile["name"],
            request.sector,
            final_score,
            final_rating,
            final_recommendation,
            factors,
            evidence,
        ), ""),
        agent_outputs=_safe("agent_outputs", lambda: build_agent_outputs(factors, evidence), []),
        workflow_steps=build_workflow_steps(),
        retrieval_results=_safe("retrieval_results", lambda: build_retrieval_context(profile["name"], request.sector, evidence), []),
        event_signals=_safe("event_signals", lambda: extract_event_signals(profile["name"], evidence), []),
        sentiment=_safe("sentiment", lambda: score_sentiment(evidence), {}),
        forecasts=_safe("forecasts", lambda: build_forecasts(evidence), []),
        model_outputs=model_outputs,
        shap_explanation=_safe("shap_explanation", lambda: build_shap_explanation(profile["name"], evidence), {}),
        confidence_interval=_safe("confidence_interval", lambda: build_confidence_interval(final_score, evidence), None),
        knowledge_graph=_safe("knowledge_graph", lambda: {
            **build_knowledge_graph(profile["name"], request.sector, factors, evidence),
            "embedding_index": build_embedding_index(evidence),
        }, {}),
        generated_at=datetime.now(timezone.utc).isoformat(),
    )

    _safe("save_assessment", lambda: save_assessment(response), None)
    return response
