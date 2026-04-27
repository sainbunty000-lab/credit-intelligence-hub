import re


def normalize_text(item: dict) -> str:
    return " ".join([
        str(item.get("location", "")),
        str(item.get("title", "")),
        str(item.get("description", ""))
    ]).lower()


def extract_value_lakh(value: str) -> float:
    if not value:
        return 0

    value = value.lower().replace(",", "").strip()

    match = re.search(r"(\d+(\.\d+)?)", value)
    if not match:
        return 0

    num = float(match.group(1))

    if "cr" in value or "crore" in value:
        return num * 100
    if "lakh" in value:
        return num

    return 0


def score_lead(item: dict) -> int:
    score = 0
    text = normalize_text(item)

    # ----------------------------
    # LOCATION (must-have signal)
    # ----------------------------
    if "gurgaon" in text or "gurugram" in text:
        score += 5
    elif "haryana" in text:
        score += 3

    # ----------------------------
    # VALUE (graduated scoring)
    # ----------------------------
    value_lakh = extract_value_lakh(item.get("value", ""))

    if value_lakh >= 1000:       # ₹10 Cr+
        score += 6
    elif value_lakh >= 500:      # ₹5 Cr+
        score += 5
    elif value_lakh >= 200:      # ₹2 Cr+
        score += 3

    # ----------------------------
    # WINNER (strongest signal)
    # ----------------------------
    if item.get("winner"):
        score += 6

    # ----------------------------
    # DEMAND (B2B)
    # ----------------------------
    if item.get("is_demand"):
        score += 5

    return score
