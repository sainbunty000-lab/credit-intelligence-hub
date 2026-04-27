import hashlib
from datetime import datetime

from services.sheets_service import SheetsService
from services.telegram_service import TelegramService

from utils.logger import logger
from utils.deduplicator import filter_new_items
from utils.winner_detector import extract_winner
from utils.lead_filter import filter_high_quality_leads
from utils.summary_builder import build_summary


# ----------------------------
# ID GENERATOR
# ----------------------------

def generate_id(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()


# ----------------------------
# SCRAPER (REPLACE WITH PLAYWRIGHT)
# ----------------------------

def scrape_all_sources():
    """
    Replace this with your actual Playwright scraping logic
    """

    # 🔴 MOCK DATA (replace with real scraping)
    return [
        {
            "title": "Road Construction Project Gurgaon",
            "location": "Gurgaon",
            "value": "₹12 Cr",
            "source": "Gov Portal",
            "url": "https://example.com/tender1",
            "description": "Contract awarded to ABC Infra Pvt Ltd for road construction"
        },
        {
            "title": "Small Repair Work Haryana",
            "location": "Haryana",
            "value": "₹50 Lakh",
            "source": "Gov Portal",
            "url": "https://example.com/tender2",
            "description": "Maintenance work"
        },
    ]


# ----------------------------
# MAIN SCRAPER LOGIC
# ----------------------------

def run_tender_scraper():
    logger.info("🚀 Starting Tender Scraper")

    sheets = SheetsService()
    telegram = TelegramService()

    existing_ids = sheets.get_existing_ids(col_index=1)

    # Step 1: Scrape
    scraped_items = scrape_all_sources()

    # Step 2: Winner Detection
    for item in scraped_items:
        text = f"{item.get('title','')} {item.get('description','')}"
        winner = extract_winner(text)

        item["winner"] = winner
        item["is_awarded"] = winner is not None

    # Step 3: HIGH ROI FILTER (Location + Value + Winner)
    filtered_items = filter_high_quality_leads(scraped_items)

    if not filtered_items:
        logger.info("❌ No high-quality leads found")
        return

    # Step 4: Deduplication
    new_items = filter_new_items(filtered_items, existing_ids)

    if not new_items:
        logger.info("✅ No new unique leads")
        return

    # Step 5: Prepare rows for Sheets
    rows = []

    for item in new_items:
        unique_key = item["title"] + item["url"]
        item_id = generate_id(unique_key)

        row = [
            item_id,
            item["title"],
            item["source"],
            item["url"],
            item.get("location", ""),
            item.get("value", ""),
            item.get("winner", ""),
            str(item.get("is_awarded", False)),
            datetime.utcnow().isoformat(),
        ]

        rows.append(row)

    # Step 6: Save to Google Sheets
    sheets.append_rows(rows)

    # Step 7: Send DAILY SUMMARY (not spam)
    summary_message = build_summary(new_items)
    telegram.send_message(summary_message)

    logger.info(f"✅ Processed {len(new_items)} high-quality leads")
