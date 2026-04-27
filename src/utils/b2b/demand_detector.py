def tag_demand(items: list) -> list:
    """
    Tag items with demand signals for B2B leads.
    
    Args:
        items: List of lead items
    
    Returns:
        Items with is_demand flag set
    """
    for item in items:
        item["is_demand"] = True  # Mark all B2B items as demand signals
    return items
