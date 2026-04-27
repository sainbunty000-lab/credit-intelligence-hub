def score_lead(item: dict) -> int:
    score = 0

    location = item.get("location", "").lower()
    value = item.get("value", "").lower()

    # Location
    if "gurgaon" in location or "gurugram" in location:
        score += 4
    elif "haryana" in location:
        score += 2

    # Value
    if "cr" in value:
        score += 4

    # Winner (tender)
    if item.get("winner"):
        score += 5

    # Demand (b2b)
    if item.get("is_demand"):
        score += 4

    return score
