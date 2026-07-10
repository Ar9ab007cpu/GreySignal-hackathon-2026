from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.schemas import AssessmentRequest, AssessmentResponse
from backend.services.countries import COUNTRY_PROFILES
from backend.services.langgraph_workflow import build_assessment_with_langgraph

app = FastAPI(
    title="GreySignal API",
    description="Geopolitical business risk intelligence API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "greysignal-api"}


@app.get("/countries")
def countries() -> list[str]:
    return [country.title() for country in sorted(COUNTRY_PROFILES.keys())]


@app.post("/assess", response_model=AssessmentResponse)
def assess(request: AssessmentRequest) -> AssessmentResponse:
    return build_assessment_with_langgraph(request)
