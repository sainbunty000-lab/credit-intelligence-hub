def score_lead(item: dict) -> int:
    score = 0

    title = item.get("title", "").lower()
    location = item.get("location", "").lower()
    value = item.get("value", "").lower()

    # ----------------------------
    # 1. LOCATION (HIGH PRIORITY)
    # ----------------------------
    if "gurgaon" in location or "gurugram" in location:
        score += 5
    elif "haryana" in location:
        score += 3

    # ----------------------------
    # 2. VALUE (₹ SIZE)
    # ----------------------------
    if "cr" in value or "crore" in value:
        score += 5
    elif "lakh" in value:
        try:
            num = float(value.split()[0])
            if num >= 200:   # 2 Cr equivalent
                score += 4
            elif num >= 50:
                score += 2
        except:
            pass

    # ----------------------------
    # 3. DEMAND SIGNAL
    # ----------------------------
    if item.get("is_demand"):
        score += 3

    # ----------------------------
    # 4. HIGH INTENT (URGENT)
    # ----------------------------
    if item.get("is_high_intent"):
        score += 4

    # ----------------------------
    # 5. WINNER SIGNAL (TENDER)
    # ----------------------------
    if item.get("winner"):
        score += 5

    # ----------------------------
    # 6. TEXT BOOST (EXTRA SIGNALS)
    # ----------------------------
    if "project" in title:
        score += 2

    if "contract" in title:
        score += 2

    if "bulk" in title:
        score += 2

    return score