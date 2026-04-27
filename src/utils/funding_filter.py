def is_target_location(item: dict) -> bool:
    text = " ".join([
        item.get("location", ""),
        item.get("title", ""),
        item.get("description", "")
    ]).lower()

    return any(k in text for k in ["gurgaon", "gurugram", "haryana"])


def is_high_value(item: dict) -> bool:
    value = item.get("value", "").lower()

    if "cr" in value:
        return True

    if "lakh" in value:
        try:
            num = float(value.split()[0])
            return num >= 200  # 2 Cr
        except:
            return False

    return False


def is_funding_opportunity(item: dict) -> bool:
    return (
        is_target_location(item)
        and is_high_value(item)
        and (item.get("winner") or item.get("is_demand"))
    )
