from __future__ import annotations

from typing import TypedDict

from typing_extensions import NotRequired

from langgraph.graph import END, START, StateGraph

from backend.schemas import AssessmentRequest, AssessmentResponse
from backend.services.risk_engine import build_assessment


class AssessmentGraphState(TypedDict):
    request: AssessmentRequest
    response: NotRequired[AssessmentResponse]
    workflow_steps: list[str]


def _initialize(state: AssessmentGraphState) -> AssessmentGraphState:
    state["workflow_steps"] = [
        "LangGraph START",
        "Initialized GreySignal assessment state",
    ]
    return state


def _run_assessment(state: AssessmentGraphState) -> AssessmentGraphState:
    response = build_assessment(state["request"])
    state["response"] = response
    state["workflow_steps"].extend(
        [
            "Collected economic, governance, weather, currency, trade, and news evidence",
            "Ran risk scoring, ML ensemble, SHAP, MAPIE, retrieval, graph, and LLM summary",
        ]
    )
    return state


def _validate_response(state: AssessmentGraphState) -> AssessmentGraphState:
    response = state.get("response")
    if response is None:
        raise RuntimeError("LangGraph workflow did not produce an assessment response.")
    state["workflow_steps"].append(f"Validated response: {response.rating}, score {response.overall_score}/100")
    return state


def _finalize(state: AssessmentGraphState) -> AssessmentGraphState:
    response = state["response"]
    response.workflow_steps = state["workflow_steps"] + response.workflow_steps + ["LangGraph END"]
    state["response"] = response
    return state


def _build_graph():
    graph = StateGraph(AssessmentGraphState)
    graph.add_node("initialize", _initialize)
    graph.add_node("run_assessment", _run_assessment)
    graph.add_node("validate_response", _validate_response)
    graph.add_node("finalize", _finalize)

    graph.add_edge(START, "initialize")
    graph.add_edge("initialize", "run_assessment")
    graph.add_edge("run_assessment", "validate_response")
    graph.add_edge("validate_response", "finalize")
    graph.add_edge("finalize", END)
    return graph.compile()


ASSESSMENT_GRAPH = _build_graph()


def build_assessment_with_langgraph(request: AssessmentRequest) -> AssessmentResponse:
    result = ASSESSMENT_GRAPH.invoke({"request": request, "workflow_steps": []})
    response = result.get("response")
    if response is None:
        raise RuntimeError("LangGraph workflow finished without an assessment response.")
    return response
