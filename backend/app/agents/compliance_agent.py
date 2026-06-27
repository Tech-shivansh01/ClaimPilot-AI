"""
compliance agent - writes the plain-english explanation for why a claim
got approved/rejected/sent to review. insurers actually need this for
real (IRDAI / regulatory stuff requires explainability), so this isn't
just a nice-to-have feature, it's the whole reason the brief mentioned it
"""
from app.services import llm_service

EXPLANATION_PROMPT = """You are writing a short, plain-English explanation for an insurance
claim decision so the claimant understands why it happened. Be direct and not overly formal.
Keep it to 3-4 sentences.

Claim decision: {status}
Reason: {reason}
Damage assessed: {damage_severity}, estimated repair cost ${repair_cost}
Fraud risk level: {risk_level} (score: {fraud_score}/100)
Payout amount: ${payout_amount}

Write the explanation now, addressed to the claimant directly:
"""


def _mock_explanation(status: str, reason: str, payout: float) -> str:
    if status == "approved":
        return (f"[mock explanation] Your claim has been approved. Based on the damage assessment, "
                f"a payout of ${payout} has been calculated after applying your policy's deductible. {reason}")
    if status == "manual_review":
        return f"[mock explanation] Your claim needs a closer look from one of our adjusters before we can decide. {reason}"
    return f"[mock explanation] Your claim could not be approved. {reason}"


def generate_explanation(state: dict) -> str:
    settlement = state.get("settlement_result", {})
    fraud = state.get("fraud_result", {})
    vision = state.get("vision_result", {})

    status = settlement.get("status", "unknown")
    reason = settlement.get("reason", "")
    payout = settlement.get("payout_amount", 0)

    if llm_service.is_mock():
        return _mock_explanation(status, reason, payout)

    try:
        prompt = EXPLANATION_PROMPT.format(
            status=status,
            reason=reason,
            damage_severity=vision.get("damage_severity", "unknown"),
            repair_cost=vision.get("estimated_repair_cost", 0),
            risk_level=fraud.get("risk_level", "unknown"),
            fraud_score=fraud.get("fraud_score", 0),
            payout_amount=payout,
        )
        return llm_service.text_chat(prompt)
    except Exception:
        return _mock_explanation(status, reason, payout)
