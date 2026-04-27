import re

# ----------------------------
# KEYWORDS (FUNDING SIGNALS)
# ----------------------------

DEMAND_KEYWORDS = [
    "require",
    "requirement",
    "looking for",
    "need",
    "wanted",
    "purchase",
    "buy",
    "supplier",
    "vendor",
    "quotation",
    "rfq",
    "tender",
    "bulk order",
    "urgent",
]

HIGH_INTENT_KEYWORDS = [
    "urgent",
    "immediate",
    "bulk",
    "large quantity",
    "contract",
    "project",
]

VALUE_PATTERNS = [
    r"\b\d+\s?cr\b",
    r"\b\d+\s?lakh\b",
    r"\b\d+\s?crore\b",
]


# ----------------------------
# DETECT DEMAND
# ----------------------------

def detect_demand(text: str) -> bool:
    text = text.lower()

    for keyword in DEMAND_KEYWORDS:
        if keyword in text:
            return True

    return False


# ----------------------------
# DETECT HIGH INTENT
# ----------------------------

def detect_high_intent(text: str) -> bool:
    text = text.lower()

    for keyword in HIGH_INTENT_KEYWORDS:
        if keyword in text:
            return True

    return False


# ----------------------------
# EXTRACT VALUE (₹ SIGNAL)
# ----------------------------

def extract_value(text: str) -> str:
    text = text.lower()

    for pattern in VALUE_PATTERNS:
        match = re.search(pattern, text)
        if match:
            return match.group()

    return ""


# ----------------------------
# MAIN TAGGING FUNCTION
# ----------------------------

def tag_demand(items: list[dict]) -> list[dict]:
    """
    Adds:
    - is_demand
    - is_high_intent
    - detected_value
    """

    for item in items:
        text = " ".join([
            item.get("title", ""),
            item.get("description", "")
        ])

        item["is_demand"] = detect_demand(text)
        item["is_high_intent"] = detect_high_intent(text)

        # extract value if not present
        if not item.get("value"):
            item["value"] = extract_value(text)

    return items
