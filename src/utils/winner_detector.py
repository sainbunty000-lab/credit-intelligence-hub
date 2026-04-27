import re
from typing import Optional


WINNER_PATTERNS = [
    r"awarded to\s*[:\-]?\s*(.+)",
    r"contract awarded to\s*[:\-]?\s*(.+)",
    r"successful bidder\s*[:\-]?\s*(.+)",
    r"L1 bidder\s*[:\-]?\s*(.+)",
    r"selected vendor\s*[:\-]?\s*(.+)",
]


def extract_winner(text: str) -> Optional[str]:
    """
    Extract winner company name from tender text
    """
    text = text.lower()

    for pattern in WINNER_PATTERNS:
        match = re.search(pattern, text)
        if match:
            winner = match.group(1).strip()
            return clean_company_name(winner)

    return None


def clean_company_name(name: str) -> str:
    """
    Clean noisy extracted company names
    """
    name = re.sub(r"\(.*?\)", "", name)  # remove brackets
    name = re.sub(r"[^a-zA-Z0-9\s&.,-]", "", name)
    return name.strip().title()
