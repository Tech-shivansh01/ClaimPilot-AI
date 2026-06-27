"""
this is the actual "agentic pipeline" part - chains the 4 agents together
using langgraph so the claim flows through vision -> documents -> fraud ->
settlement -> compliance as a graph instead of just calling functions in a
row. kept it as a straight line for now (no branching/looping back), could
extend it later e.g. branch the fraud check could send it back for more docs
"""
from typing import TypedDict, List, Optional, Any

from langgraph.graph import StateGraph, END

from app.agents.vision_agent import analyze_photos
from app.agents.document_agent import extract_documents
from app.agents.fraud_agent import run_fraud_checks
from app.agents.settlement_agent import calculate_settlement
from app.agents.compliance_agent import generate_explanation


class ClaimState(TypedDict):
    claim_id: int
    policy_number: str
    incident_date: str
    incident_location: str
    description: str
    photo_paths: List[str]
    document_paths: List[dict]

    # policy context needed by fraud/settlement steps
    registered_location: Optional[str]
    coverage_limit: float
    deductible: float
    policy_active: bool
    days_since_policy_start: int
    historical_claim_count: int

    # filled in as the pipeline runs
    vision_result: Optional[dict]
    document_result: Optional[dict]
    fraud_result: Optional[dict]
    settlement_result: Optional[dict]
    explanation: Optional[str]
    final_status: Optional[str]


def vision_step(state: ClaimState) -> ClaimState:
    state["vision_result"] = analyze_photos(state["photo_paths"])
    return state


def document_step(state: ClaimState) -> ClaimState:
    state["document_result"] = extract_documents(state["document_paths"])
    return state


def fraud_step(state: ClaimState) -> ClaimState:
    state["fraud_result"] = run_fraud_checks(state)
    return state


def settlement_step(state: ClaimState) -> ClaimState:
    state["settlement_result"] = calculate_settlement(state)
    return state


def compliance_step(state: ClaimState) -> ClaimState:
    state["explanation"] = generate_explanation(state)
    state["final_status"] = state["settlement_result"]["status"]
    return state


def _build_graph():
    graph = StateGraph(ClaimState)
    graph.add_node("vision", vision_step)
    graph.add_node("documents", document_step)
    graph.add_node("fraud_check", fraud_step)
    graph.add_node("settlement", settlement_step)
    graph.add_node("compliance", compliance_step)

    graph.set_entry_point("vision")
    graph.add_edge("vision", "documents")
    graph.add_edge("documents", "fraud_check")
    graph.add_edge("fraud_check", "settlement")
    graph.add_edge("settlement", "compliance")
    graph.add_edge("compliance", END)

    return graph.compile()


_compiled_pipeline = _build_graph()


def run_claim_pipeline(initial_state: dict) -> dict:
    return _compiled_pipeline.invoke(initial_state)
