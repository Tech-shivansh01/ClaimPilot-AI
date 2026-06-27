"""
vision agent - looks at the accident photos and estimates damage.
uses gpt-4o vision. tried out grounding dino + sam2 for actual part
segmentation first but couldn't get them running without a gpu, so
went with a vision-language model approach instead which honestly
worked better for getting a cost estimate anyway since it can reason
about it instead of just drawing boxes
"""
from app.services import llm_service

VISION_PROMPT = """You are an auto insurance damage assessor. Look at this accident photo
and respond with ONLY a JSON object in this exact format:
{
  "damage_severity": "minor" | "moderate" | "severe",
  "parts_affected": ["list", "of", "car", "parts"],
  "estimated_repair_cost": <number in USD>,
  "notes": "one short sentence about what you see"
}
"""


def _mock_result(photo_path: str) -> dict:
    # not actually random based on the image, just cycles through a few
    # plausible-looking demo results so the UI has something to show
    import hashlib
    seed = int(hashlib.md5(photo_path.encode()).hexdigest(), 16) % 3
    options = [
        {"damage_severity": "minor", "parts_affected": ["front bumper"], "estimated_repair_cost": 450,
         "notes": "[mock] small scratch/dent on bumper, no key parts seem affected"},
        {"damage_severity": "moderate", "parts_affected": ["front bumper", "headlight", "hood"],
         "estimated_repair_cost": 1800, "notes": "[mock] front-end collision, headlight likely needs replacement"},
        {"damage_severity": "severe", "parts_affected": ["front bumper", "hood", "headlight", "radiator", "fender"],
         "estimated_repair_cost": 6200, "notes": "[mock] heavy front impact, possible frame damage"},
    ]
    return options[seed]


def analyze_single_photo(photo_path: str) -> dict:
    if llm_service.is_mock():
        result = _mock_result(photo_path)
        result["mock_mode"] = True
        return result

    try:
        result = llm_service.vision_chat(photo_path, VISION_PROMPT)
        result["mock_mode"] = False
        return result
    except Exception as e:
        # if the api call fails for whatever reason, don't blow up the whole pipeline
        fallback = _mock_result(photo_path)
        fallback["mock_mode"] = True
        fallback["error"] = str(e)
        return fallback


def analyze_photos(photo_paths: list[str]) -> dict:
    if not photo_paths:
        return {"damage_severity": "unknown", "parts_affected": [], "estimated_repair_cost": 0,
                "notes": "no photos were uploaded", "per_photo": []}

    per_photo = [analyze_single_photo(p) for p in photo_paths]

    # take the worst severity across all photos and sum up the cost estimates
    severity_rank = {"minor": 1, "moderate": 2, "severe": 3, "unknown": 0}
    worst = max(per_photo, key=lambda r: severity_rank.get(r["damage_severity"], 0))

    all_parts = sorted(set(p for r in per_photo for p in r.get("parts_affected", [])))
    total_cost = sum(r.get("estimated_repair_cost", 0) for r in per_photo)

    return {
        "damage_severity": worst["damage_severity"],
        "parts_affected": all_parts,
        "estimated_repair_cost": total_cost,
        "per_photo": per_photo,
    }
