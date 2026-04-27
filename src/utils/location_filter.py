def is_target_location(item: dict) -> bool:
    """
    Filter tenders for Gurgaon / Gurugram / Haryana
    """

    location = (
        (item.get("location", "") + " " +
         item.get("title", "") + " " +
         item.get("description", ""))
        .lower()
    )

    keywords = [
        "gurgaon",
        "gurugram",
        "haryana",
    ]

    return any(keyword in location for keyword in keywords)
