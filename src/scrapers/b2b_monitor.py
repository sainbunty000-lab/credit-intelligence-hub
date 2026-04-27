import hashlib
from datetime import datetime

from services.sheets_service import SheetsService
from services.telegram_service import TelegramService

from utils.logger import logger
from utils.deduplicator import filter_new_items

from utils.b2b.demand_detector import tag_demand
from utils.funding_filter import is_funding_opportunity
from utils.lead_scorer import score_lead


# ----------------------------
# ID GENERATOR
# ----------------------------
def generate_id(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()


# ----------------------------
# SCRAPER (REPLACE WITH REAL DATA)
# ----------------------------
def scrape_b2b_sources():
    return []  # TODO: implement


# ----------------------------
# MAIN
# ----------------------------
def run_b2b_monitor():
    logger.info("🚀 B2B Monitor Started")

    sheets = SheetsService()
    telegram = TelegramService()

    existing_ids = sheets.get_existing_ids(col_index=1)

    items = scrape_b2b_sources()

    if not items:
        logger.info("❌ No B2B data found")
        return

    # ----------------------------
    # Demand Detection
    # ----------------------------
    items = tag_demand(items)

    # ----------------------------
    # Funding Filter
    # ----------------------------
    items = [i for i in items if is_funding_opportunity(i)]

    if not items:
        logger.info("❌ No funding opportunities (B2B)")
        return

    # ----------------------------
    # Scoring
    # ----------------------------
    for item in items:
        item["score"] = score_lead(item)

    # Sort by score
    items = sorted(items, key=lambda x: x["score"], reverse=True)

    # Take TOP 3
    top_items = items[:3]

    # ----------------------------
    # Deduplication
    # ----------------------------
    new_items = filter_new_items(top_items, existing_ids)

    if not new_items:
        logger.info("✅ No new B2B leads")
        return

    # ----------------------------
    # Save to Sheets
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
    # Telegram Output
    # ----------------------------
    message = "📦 *TOP FUNDING OPPORTUNITIES (B2B)*\n\n"

    for i, item in enumerate(new_items, 1):
        message += (
            f"{i}. *{item['title']}*\n"
            f"📦 Demand\n"
            f"💰 {item.get('value','N/A')}\n"
            f"📍 {item.get('location','N/A')}\n\n"
        )

    message += "👉 Action: Call immediately"

    telegram.send_message(message)

    logger.info(f"✅ {len(new_items)} B2B leads sent")
