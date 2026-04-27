import re


def normalize_text(item: dict) -> str:
    return " ".join([
        str(item.get("location", "")),
        str(item.get("title", "")),
        str(item.get("description", ""))
    ]).lower()


# ----------------------------
# LOCATION FILTER
# ----------------------------
def is_target_location(item: dict) -> bool:
    text = normalize_text(item)

    keywords = [
        "gurgaon",
        "gurugram",
        "haryana",
        "hr-"  # sometimes used in tender codes
    ]

    return any(k in text for k in keywords)


# ----------------------------
# VALUE PARSER (ROBUST)
# ----------------------------
def extract_value_number(value: str) -> float:
    """
    Convert value text → number in lakhs
    Example:
    ₹12 Cr → 1200
    ₹50 Lakh → 50
    """
    if not value:
        return 0

    value = value.lower().replace(",", "").strip()

    # Match number
    match = re.search(r"(\d+(\.\d+)?)", value)
    if not match:
        return 0

    num = float(match.group(1))

    if "cr" in value or "crore" in value:
        return num * 100  # convert to lakh

    if "lakh" in value:
        return num

    return 0


# ----------------------------
# HIGH VALUE FILTER
# ----------------------------
def is_high_value(item: dict, min_lakh: float = 200) -> bool:
    """
    Default: ₹2 Cr (200 lakh)
    """
    value_text = item.get("value", "")
    value_lakh = extract_value_number(value_text)

    return value_lakh >= min_lakh


# ----------------------------
# FINAL FUNDING FILTER
# ----------------------------
def is_funding_opportunity(item: dict) -> bool:
    """
    FINAL BUSINESS RULE:
    Gurgaon/Haryana + High Value + (Winner OR Demand)
    """

    has_signal = item.get("winner") or item.get("is_demand")

    return (
        is_target_location(item)
        and is_high_value(item)
        and has_signal
    )
