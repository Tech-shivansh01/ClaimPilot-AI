"""
settlement agent - mostly straightforward business rules, no AI needed
here really. coverage eligibility + payout math. the brief called it an
"agent" so it lives next to the others, but it's deterministic on purpose -
insurers want explainable math here, not a model deciding payouts

this now actually uses what the document agent extracted instead of just
throwing it away after extraction:
- a real repair estimate quote (if uploaded) overrides the vision agent's
  photo-based guess, since an actual shop quote is more authoritative
- a medical report's cost gets added on top as a separate compensation
  category (covers injury costs, not vehicle repair)
"""
from app.config import settings


def _get_repair_cost(state: dict) -> float:
    """prefer a real repair estimate document over the vision agent's guess from photos"""
    vision_estimate = state.get("vision_result", {}).get("estimated_repair_cost", 0)

    documents = state.get("document_result", {}).get("documents", [])
    for doc in documents:
        if doc.get("doc_type") == "repair_estimate" and doc.get("amount_mentioned"):
            return float(doc["amount_mentioned"])

    return vision_estimate


def _get_medical_costs(state: dict) -> float:
    """sums up amounts from any medical report documents - this is on top of
    repair cost, not instead of it, since it's compensating a different thing"""
    documents = state.get("document_result", {}).get("documents", [])
    total = 0.0
    for doc in documents:
        if doc.get("doc_type") == "medical_report" and doc.get("amount_mentioned"):
            total += float(doc["amount_mentioned"])
    return total


def calculate_settlement(state: dict) -> dict:
    repair_cost = _get_repair_cost(state)
    medical_costs = _get_medical_costs(state)
    total_claim_amount = repair_cost + medical_costs

    coverage_limit = state.get("coverage_limit", 100000)
    deductible = state.get("deductible", 2000)
    fraud_score = state.get("fraud_result", {}).get("fraud_score", 0)
    policy_active = state.get("policy_active", True)

    if not policy_active:
        return {
            "status": "rejected",
            "payout_amount": 0,
            "reason": "policy is not active for the incident date",
        }

    if fraud_score >= settings.FRAUD_REVIEW_THRESHOLD:
        return {
            "status": "manual_review",
            "payout_amount": 0,
            "reason": f"fraud score ({fraud_score}) crossed the review threshold ({settings.FRAUD_REVIEW_THRESHOLD}), needs a human adjuster",
        }

    payout = max(0, total_claim_amount - deductible)
    payout = min(payout, coverage_limit)

    if payout <= 0:
        return {
            "status": "rejected",
            "payout_amount": 0,
            "reason": "estimated claim amount doesn't exceed the policy deductible",
        }

    cost_breakdown = f"${repair_cost:.0f} repair cost"
    if medical_costs > 0:
        cost_breakdown += f" + ${medical_costs:.0f} medical costs"

    return {
        "status": "approved",
        "payout_amount": round(payout, 2),
        "reason": f"{cost_breakdown}, minus ${deductible:.0f} deductible, capped at ${coverage_limit:.0f} coverage limit",
    }
