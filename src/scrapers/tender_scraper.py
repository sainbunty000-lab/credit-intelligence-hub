import hashlib
from datetime import datetime

from services.sheets_service import SheetsService
from services.telegram_service import TelegramService
from utils.logger import logger


def generate_id(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()


def scrape_tenders():
    """
    Replace this with your actual Playwright scraping logic
    Return list of dicts
    """
    # 🔴 MOCK DATA (replace with real scraper)
    return [
        {
            "title": "Road Construction Tender",
            "location": "Delhi",
            "value": "₹2 Cr",
            "source": "Gov Portal",
            "url": "https://example.com/tender1",
        },
        {
            "title": "Bridge Repair Tender",
            "location": "Mumbai",
            "value": "₹5 Cr",
            "source": "Gov Portal",
            "url": "https://example.com/tender2",
        },
    ]


def run_tender_scraper():
    logger.info("🚀 Starting Tender Scraper")

    sheets = SheetsService()
    telegram = TelegramService()

    # Fetch existing IDs for deduplication
    existing_ids = sheets.get_existing_ids(col_index=1)

    scraped_items = scrape_tenders()

    new_rows = []
    messages = []

    for item in scraped_items:
        unique_string = item["title"] + item["url"]
        item_id = generate_id(unique_string)

        if item_id in existing_ids:
            continue

        row = [
            item_id,
            item["title"],
            item["source"],
            item["url"],
            item.get("location", ""),
            item.get("value", ""),
            datetime.utcnow().isoformat(),
        ]

        new_rows.append(row)

        message = telegram.format_tender(item)
        messages.append(message)

    if not new_rows:
        logger.info("✅ No new tenders found")
        return

    # Save to Sheets first
    sheets.append_rows(new_rows)

    # Then notify
    telegram.send_bulk_messages(messages)

    logger.info(f"✅ Processed {len(new_rows)} new tenders")
