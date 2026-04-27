def is_high_value(item: dict, min_value: int = 20000000) -> bool:
    """
    Filter tenders above ₹2 Cr (adjustable)
    """
    value_text = item.get("value", "").lower()

    # crude parsing (can improve later)
    if "cr" in value_text:
        return True

    if "lakh" in value_text:
        try:
            num = float(value_text.split()[0])
            return num >= 200  # 200 lakh = 2 Cr
        except:
            return False

    return False


def is_target_location(item: dict) -> bool:
    text = " ".join([
        item.get("location", ""),
        item.get("title", ""),
        item.get("description", "")
    ]).lower()

    return any(k in text for k in ["gurgaon", "gurugram", "haryana"])


def is_winner_available(item: dict) -> bool:
    return bool(item.get("winner"))


def filter_high_quality_leads(items: list[dict]) -> list[dict]:
    """
    FINAL FILTER:
    Location + Value + Winner
    """
    results = []

    for item in items:
        if not is_target_location(item):
            continue

        if not is_high_value(item):
            continue

        if not is_winner_available(item):
            continue

        results.append(item)

    return results
