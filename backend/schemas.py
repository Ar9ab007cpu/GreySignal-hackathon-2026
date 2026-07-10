from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AssessmentRequest(BaseModel):
    country: str = Field(..., examples=["Vietnam"])
    sector: str = Field("General business expansion")
    city: Optional[str] = Field(None, examples=["Ho Chi Minh City"])
    city_or_port: Optional[str] = Field(None, examples=["Hai Phong"])
    investment_size: str = Field("Medium", examples=["Small", "Medium", "Large"])
    entry_mode: str = Field("Greenfield", examples=["Exporting", "Joint venture", "Greenfield", "Acquisition"])
    time_horizon: str = Field("12-24 months", examples=["0-6 months", "6-12 months", "12-24 months", "24+ months"])
    risk_tolerance: str = Field("Medium", examples=["Low", "Medium", "High"])
    labor_intensity: str = Field("Medium", examples=["Low", "Medium", "High"])
    supply_chain_dependence: str = Field("Medium", examples=["Low", "Medium", "High"])
    regulatory_sensitivity: str = Field("Medium", examples=["Low", "Medium", "High"])
    local_partner_available: bool = Field(False)
    news_keywords: str = Field("strike OR protest OR election OR tariff OR supply chain")
    base_currency: str = Field("USD", min_length=3, max_length=3)
    target_currency: str = Field("VND", min_length=3, max_length=3)
    hs_code: str = Field("TOTAL", examples=["85", "8542", "TOTAL"])
    start_year: int = Field(2020, ge=1960, le=2100)
    end_year: int = Field(2026, ge=1960, le=2100)


class EvidenceItem(BaseModel):
    source: str
    label: str
    value: str
    status: str = "ok"
    detail: str = ""


class RiskFactor(BaseModel):
    name: str
    score: float = Field(..., ge=0, le=100)
    weight: float = Field(..., ge=0, le=1)
    rationale: str


class AgentOutput(BaseModel):
    agent: str
    finding: str
    confidence: float = Field(..., ge=0, le=1)


class RetrievalResult(BaseModel):
    source: str
    text: str
    score: float


class EventSignal(BaseModel):
    category: str
    entity: str
    evidence: str


class ForecastPoint(BaseModel):
    label: str
    current: Optional[float] = None
    forecast: Optional[float] = None
    direction: str


class ConfidenceInterval(BaseModel):
    lower: float = Field(..., ge=0, le=100)
    upper: float = Field(..., ge=0, le=100)
    method: str


class AssessmentResponse(BaseModel):
    country: str
    sector: str
    overall_score: float = Field(..., ge=0, le=100)
    rating: str
    recommendation: str
    summary: str
    factors: List[RiskFactor]
    evidence: List[EvidenceItem]
    ai_summary: str = ""
    agent_outputs: List[AgentOutput] = []
    workflow_steps: List[str] = []
    retrieval_results: List[RetrievalResult] = []
    event_signals: List[EventSignal] = []
    sentiment: Dict[str, Any] = {}
    forecasts: List[ForecastPoint] = []
    model_outputs: Dict[str, float] = {}
    shap_explanation: Dict[str, float] = {}
    confidence_interval: Optional[ConfidenceInterval] = None
    knowledge_graph: Dict[str, Any] = {}
    generated_at: str
