"""
fraud agent.

note: the original idea was a graph neural network looking at relationships
between claims/policies/garages etc. realistically that needs a labeled
historical claims graph dataset which doesn't exist for a solo/college
project, so I went with something I could actually justify in an interview:
a handful of rule-based checks (tampered image metadata, location mismatch,
duplicate claim via the vector store) combined with an IsolationForest
anomaly score over basic claim features. still "anomaly detection" like the
brief asked for, just without pretending there's a trained GNN behind it.
"""
import difflib

import numpy as np
from sklearn.ensemble import IsolationForest

from app.services import vector_store

# little bit of synthetic "historical" data to fit the anomaly model on at
# import time, since we obviously don't have years of real claims data.
# features: [claim_amount, days_since_policy_start, historical_claim_count]
_SYNTHETIC_HISTORY = np.array([
    [800, 400, 0], [1200, 600, 1], [2000, 900, 0], [500, 200, 0],
    [3000, 1500, 2], [1500, 700, 1], [900, 300, 0], [2500, 1000, 1],
    [600, 150, 0], [1800, 800, 1], [4000, 2000, 2], [1100, 500, 0],
])

_anomaly_model = IsolationForest(contamination=0.15, random_state=42)
_anomaly_model.fit(_SYNTHETIC_HISTORY)


def _check_image_tampering(photo_paths: list[str]) -> dict:
    """crude check - just looks for an editing-software tag in EXIF data.
    real tamper detection would need ELA / pixel-level forensics, this is
    the simple version that's actually feasible without a specialized model"""
    from PIL import Image

    flagged = []
    for path in photo_paths:
        try:
            img = Image.open(path)
            exif = img.getexif()
            software = exif.get(305)  # 305 = "Software" exif tag
            if software and any(tag in str(software).lower() for tag in ["photoshop", "gimp", "lightroom"]):
                flagged.append({"file": path, "reason": f"EXIF software tag: {software}"})
        except Exception:
            continue
    return {"flagged_images": flagged, "tampering_suspected": len(flagged) > 0}


def _check_location_mismatch(incident_location: str, registered_location: str) -> dict:
    if not incident_location or not registered_location:
        return {"mismatch": False, "note": "not enough location info to compare"}

    ratio = difflib.SequenceMatcher(None, incident_location.lower(), registered_location.lower()).ratio()
    mismatch = ratio < 0.3
    return {"mismatch": mismatch, "similarity": round(ratio, 2)}


def _check_duplicate_claims(claim_id: int, description: str) -> dict:
    similar = vector_store.find_similar_claims(description, exclude_claim_id=claim_id)
    return {"possible_duplicates": similar, "duplicate_suspected": len(similar) > 0}


def _anomaly_score(claim_amount: float, days_since_policy_start: int, historical_claim_count: int) -> float:
    features = np.array([[claim_amount, days_since_policy_start, historical_claim_count]])
    # decision_function: higher = more normal, lower/negative = more anomalous
    raw_score = _anomaly_model.decision_function(features)[0]
    # squash into a 0-100 "risk" scale, roughly
    risk = max(0, min(100, (0.5 - raw_score) * 100))
    return round(risk, 1)


def run_fraud_checks(state: dict) -> dict:
    claim_amount = state.get("vision_result", {}).get("estimated_repair_cost", 0)
    days_since_start = state.get("days_since_policy_start", 365)
    historical_count = state.get("historical_claim_count", 0)

    tampering = _check_image_tampering(state.get("photo_paths", []))
    location = _check_location_mismatch(state.get("incident_location", ""), state.get("registered_location", ""))
    duplicates = _check_duplicate_claims(state["claim_id"], state.get("description", ""))
    anomaly_risk = _anomaly_score(claim_amount, days_since_start, historical_count)

    # combine everything into one score, weights are just gut-feel, not tuned on real data
    score = anomaly_risk * 0.5
    if tampering["tampering_suspected"]:
        score += 25
    if location["mismatch"]:
        score += 15
    if duplicates["duplicate_suspected"]:
        score += 20
    score = round(min(100, score), 1)

    risk_level = "low" if score < 35 else "medium" if score < 70 else "high"

    return {
        "fraud_score": score,
        "risk_level": risk_level,
        "checks": {
            "image_tampering": tampering,
            "location_mismatch": location,
            "duplicate_claims": duplicates,
            "anomaly_score": anomaly_risk,
        },
    }
