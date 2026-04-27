import hashlib
from datetime import datetime

from services.sheets_service import SheetsService
from services.telegram_service import TelegramService

from utils.logger import logger
from utils.deduplicator import filter_new_items
from utils.lead_scorer import score_lead
from utils.b2b.demand_detector import tag_demand


# ----------------------------
# ID GENERATOR
# ----------------------------
def generate_id(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()


# ----------------------------
# REAL SCRAPER (PLACEHOLDER LIVE STRUCTURE)
# ----------------------------
def scrape_b2b_sources():
    # Replace later with Playwright / API
    return [
        {
            "title": "Urgent requirement: Need steel supplier for Gurgaon construction project (3 Cr)",
            "description": "Looking for vendor for bulk supply. Immediate requirement.",
            "location": "Gurgaon",
            "value": "",
            "url": "https://example.com/lead1",
            "source": "IndiaMART",
        },
        {
            "title": "Bulk order for agricultural supply - Haryana (2 Cr)",
            "description": "Need supplier for large quantity purchase",
            "location": "Haryana",
            "value": "",
            "url": "https://example.com/lead2",
            "source": "TradeIndia",
        },
    ]


# ----------------------------
# MAIN
# ----------------------------
def run_b2b_monitor():
    logger.info("🚀 B2B Monitor Started")

    sheets = SheetsService()
    telegram = TelegramService()

    existing_ids = sheets.get_existing_ids()

    # ----------------------------
    # SCRAPE
    # ----------------------------
    items = scrape_b2b_sources()
    logger.info(f"DEBUG: Scraped = {len(items)}")

    if not items:
        return

    # ----------------------------
    # DEMAND + INTENT TAGGING
    # ----------------------------
    items = tag_demand(items)

    # ----------------------------
    # FILTER (REAL LOGIC)
    # ----------------------------
    filtered_items = [
        i for i in items
        if i.get("is_demand")  # must be demand
    ]

    logger.info(f"DEBUG: After demand filter = {len(filtered_items)}")

    if not filtered_items:
        return

    # ----------------------------
    # SCORING
    # ----------------------------
    for item in filtered_items:
        item["score"] = score_lead(item)

    # ----------------------------
    # PRIORITY FILTER (IMPORTANT)
    # Only strong leads
    # ----------------------------
    filtered_items = [i for i in filtered_items if i["score"] >= 5]

    logger.info(f"DEBUG: After score filter = {len(filtered_items)}")

    if not filtered_items:
        logger.info("❌ No high-quality leads")
        return

    # ----------------------------
    # SORT + TOP
    # ----------------------------
    top_items = sorted(filtered_items, key=lambda x: x["score"], reverse=True)[:3]

    # ----------------------------
    # DEDUP
    # ----------------------------
    new_items = filter_new_items(top_items, existing_ids)
    logger.info(f"DEBUG: New = {len(new_items)}")

    if not new_items:
        return

    # ----------------------------
    # SAVE
    # ----------------------------
    rows = []
    for item in new_items:
        item_id = generate_id(item["title"] + item["url"])

        rows.append([
            item_id,
            item["title"],
            item["source"],
            item["url"],
            item.get("location", ""),
            item.get("value", ""),
            "DEMAND",
            "True",
            datetime.utcnow().isoformat(),
        ])

    sheets.append_rows(rows)

    # ----------------------------
    # TELEGRAM (HIGH QUALITY ONLY)
    # ----------------------------
    message = "📦 *HIGH PRIORITY FUNDING LEADS (B2B)*\n\n"

    for i, item in enumerate(new_items, 1):
        message += (
            f"{i}. *{item['title']}*\n"
            f"📍 {item.get('location','N/A')}\n"
            f"💰 {item.get('value','N/A')}\n"
            f"🔥 Score: {item['score']}\n\n"
        )

    message += "👉 Action: Call immediately"

    telegram.send_message(message)

    logger.info(f"✅ {len(new_items)} B2B leads sent")