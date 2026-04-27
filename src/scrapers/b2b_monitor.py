import hashlib
from datetime import datetime

from services.sheets_service import SheetsService
from services.telegram_service import TelegramService
from utils.logger import logger


def generate_id(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()


def scrape_b2b_leads():
    """
    Replace with actual Playwright scraping
    """
    # 🔴 MOCK DATA (replace with real logic)
    return [
        {
            "title": "Bulk Cement Requirement",
            "location": "Chennai",
            "value": "₹50 Lakhs",
            "source": "B2B Portal",
            "url": "https://example.com/lead1",
        },
        {
            "title": "IT Services Contract",
            "location": "Bangalore",
            "value": "₹1 Cr",
            "source": "B2B Portal",
            "url": "https://example.com/lead2",
        },
    ]


def format_b2b_message(item: dict) -> str:
    return (
        f"*{item['title']}*\n\n"
        f"📍 Location: {item.get('location', 'N/A')}\n"
        f"💰 Value: {item.get('value', 'N/A')}\n"
        f"🏢 Source: {item.get('source', 'N/A')}\n\n"
        f"[🔗 View Lead]({item.get('url', '')})"
    )


def run_b2b_monitor():
    logger.info("🚀 Starting B2B Monitor")

    sheets = SheetsService()
    telegram = TelegramService()

    existing_ids = sheets.get_existing_ids(col_index=1)

    scraped_items = scrape_b2b_leads()

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

        message = format_b2b_message(item)
        messages.append(message)

    if not new_rows:
        logger.info("✅ No new B2B leads found")
        return

    sheets.append_rows(new_rows)
    telegram.send_bulk_messages(messages)

    logger.info(f"✅ Processed {len(new_rows)} new B2B leads")
