PRIORITY_KEYWORDS = [
    "construction",
    "infrastructure",
    "road",
    "bridge",
    "government",
    "contract",
    "tender",
    "supply",
]

LOW_PRIORITY_KEYWORDS = [
    "small",
    "repair",
    "maintenance",
]


def score_item(item: dict) -> int:
    text = (item.get("title", "") + " " + item.get("description", "")).lower()

    score = 0

    for word in PRIORITY_KEYWORDS:
        if word in text:
            score += 2

    for word in LOW_PRIORITY_KEYWORDS:
        if word in text:
            score -= 1

    return score


def filter_high_priority(items: list[dict], threshold: int = 2):
    return [item for item in items if score_item(item) >= threshold]
