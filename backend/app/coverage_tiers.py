"""
real insurers set the coverage limit and deductible based on which plan
you buy - the customer doesn't get to type in their own numbers. this is
that plan list. amounts are in USD (the app's base currency for storage,
converted for display elsewhere depending on the currency toggle).
"""

COVERAGE_TIERS = {
    "third_party": {
        "label": "Third Party Only",
        "coverage_limit": 50000,
        "deductible": 1000,
        "description": "Covers damage to others. Cheapest plan, lowest payout ceiling.",
    },
    "third_party_plus": {
        "label": "Third Party Plus",
        "coverage_limit": 100000,
        "deductible": 750,
        "description": "Third party cover plus some damage to your own vehicle.",
    },
    "comprehensive": {
        "label": "Comprehensive",
        "coverage_limit": 200000,
        "deductible": 500,
        "description": "Full cover, highest payout ceiling, lowest deductible.",
    },
}

DEFAULT_TIER = "comprehensive"
