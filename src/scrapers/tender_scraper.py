import hashlib
from datetime import datetime

from services.sheets_service import SheetsService
from services.telegram_service import TelegramService

from utils.logger import logger
from utils.deduplicator import filter_new_items

from utils.tender.winner_detector import extract_winner
from utils.funding_filter import is_funding_opportunity
from utils.lead_scorer import score_lead


# ----------------------------
# ID GENERATOR
# ----------------------------
def generate_id(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()


# ----------------------------
# SCRAPER (REPLACE WITH PLAYWRIGHT)
# ----------------------------
def scrape_all_sources():
    return []  # TODO: implement


# ----------------------------
# MAIN
# ----------------------------
def run_tender_scraper():
    logger.info("🚀 Tender Scraper Started")

    sheets = SheetsService()
    telegram = TelegramService()

    existing_ids = sheets.get_existing_ids(col_index=1)

    items = scrape_all_sources()

    if not items:
        logger.info("❌ No tenders found")
        return

    # ----------------------------
    # Winner Detection
    # ----------------------------
    for item in items:
        text = item.get("title", "") + " " + item.get("description", "")
        item["winner"] = extract_winner(text)

    # ----------------------------
    # Funding Filter
    # ----------------------------
    items = [i for i in items if is_funding_opportunity(i)]

    if not items:
        logger.info("❌ No funding opportunities (tender)")
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
        logger.info("✅ No new tender leads")
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
            item.get("winner", ""),
            "True",
            datetime.utcnow().isoformat(),
        ])

    sheets.append_rows(rows)

    # ----------------------------
    # Telegram Output (TOP DEALS)
    # ----------------------------
    message = "🔥 *TOP FUNDING OPPORTUNITIES (TENDER)*\n\n"

    for i, item in enumerate(new_items, 1):
        message += (
            f"{i}. *{item['title']}*\n"
            f"🏆 Winner: {item.get('winner','N/A')}\n"
            f"💰 {item.get('value','N/A')}\n"
            f"📍 {item.get('location','N/A')}\n\n"
        )

    message += "👉 Action: Call immediately"

    telegram.send_message(message)

    logger.info(f"✅ {len(new_items)} tender leads sent")
