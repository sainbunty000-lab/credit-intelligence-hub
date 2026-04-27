import hashlib
from typing import List, Dict, Set


def generate_id(text: str) -> str:
    """
    Generate a stable unique ID using MD5 hash
    """
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def build_unique_key(item: Dict) -> str:
    """
    Create a unique string from item fields
    Modify this if your structure changes
    """
    title = item.get("title", "")
    url = item.get("url", "")

    return f"{title.strip()}|{url.strip()}"


def filter_new_items(
    items: List[Dict],
    existing_ids: Set[str],
) -> List[Dict]:
    """
    Filter out already existing items using IDs

    Returns only NEW items
    """

    new_items = []

    for item in items:
        unique_key = build_unique_key(item)
        item_id = generate_id(unique_key)

        if item_id in existing_ids:
            continue

        item["id"] = item_id  # attach ID for downstream use
        new_items.append(item)

    return new_items
