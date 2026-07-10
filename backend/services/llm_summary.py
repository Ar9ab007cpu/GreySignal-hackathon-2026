from __future__ import annotations

from typing import Sequence

import requests

from backend.config import settings
from backend.schemas import AssessmentRequest, EvidenceItem, RiskFactor


def build_groq_summary(
    request: AssessmentRequest,
    country: str,
    sector: str,
    score: float,
    rating: str,
    recommendation: str,
    factors: Sequence[RiskFactor],
    evidence: Sequence[EvidenceItem],
) -> str:
    if not settings.groq_api_key or not settings.groq_api_url:
        return ""

    factor_lines = "\n".join(f"- {factor.name}: {factor.score}/100. {factor.rationale}" for factor in factors)
    evidence_lines = "\n".join(
        f"- {item.source} | {item.label} | {item.status} | {item.value} | {item.detail[:180]}" for item in evidence
    )
    context_lines = f"""
City/port: {request.city_or_port or request.city or "not specified"}
Investment size: {request.investment_size}
Entry mode: {request.entry_mode}
Time horizon: {request.time_horizon}
Risk tolerance: {request.risk_tolerance}
Labor intensity: {request.labor_intensity}
Supply-chain dependence: {request.supply_chain_dependence}
Regulatory sensitivity: {request.regulatory_sensitivity}
Local partner available: {request.local_partner_available}
News keywords: {request.news_keywords}
""".strip()
    prompt = f"""
Create a concise executive risk brief for a company considering {sector} in {country}.
Overall score: {score}/100
Rating: {rating}
Recommendation: {recommendation}

Business context:
{context_lines}

Risk factors:
{factor_lines}

Evidence:
{evidence_lines}

Return:
1. Decision view
2. Top 3 risks
3. Mitigations
4. Evidence caveats
""".strip()

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": "You are a geopolitical business risk analyst. Be precise and evidence-led."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 500,
    }
    headers = {"Authorization": f"Bearer {settings.groq_api_key}", "Content-Type": "application/json"}

    try:
        response = requests.post(
            settings.groq_api_url,
            headers=headers,
            json=payload,
            timeout=settings.http_timeout_seconds,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except (requests.RequestException, KeyError, IndexError, TypeError) as exc:
        return f"AI summary unavailable: {exc}"
