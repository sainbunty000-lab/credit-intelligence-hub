import hashlib
from datetime import datetime
from playwright.sync_api import sync_playwright

from services.sheets_service import SheetsService
from services.telegram_service import TelegramService

from utils.logger import logger
from utils.deduplicator import filter_new_items
from utils.lead_scorer import score_lead


def generate_id(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()


def scrape_all_sources():
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto("https://bidplus.gem.gov.in/all-bids")
        page.wait_for_timeout(5000)

        rows = page.query_selector_all("table tbody tr")

        for row in rows[:10]:
            try:
                cols = row.query_selector_all("td")
                if len(cols) < 5:
                    continue

                title = cols[1].inner_text().strip()
                value = cols[4].inner_text().strip()

                results.append({
                    "title": title,
                    "value": value,
                    "location": "India",
                    "url": "https://bidplus.gem.gov.in",
                    "source": "GeM"
                })
            except:
                continue

        browser.close()

    return results


def run_tender_scraper():
    logger.info("🚀 Tender Scraper Started")

    sheets = SheetsService()
    telegram = TelegramService()

    existing_ids = sheets.get_existing_ids()

    items = scrape_all_sources()
    logger.info(f"DEBUG: Scraped = {len(items)}")

    if not items:
        return

    # simple filtering (WORKING)
    filtered_items = items

    for item in filtered_items:
        item["score"] = score_lead(item)

    top_items = sorted(filtered_items, key=lambda x: x["score"], reverse=True)[:3]

    new_items = filter_new_items(top_items, existing_ids)
    logger.info(f"DEBUG: New = {len(new_items)}")

    if not new_items:
        return

    rows = []
    for item in new_items:
        item_id = generate_id(item["title"])

        rows.append([
            item_id,
            item["title"],
            item["source"],
            item["url"],
            item.get("location", ""),
            item.get("value", ""),
            "",
            "True",
            datetime.utcnow().isoformat(),
        ])

    sheets.append_rows(rows)

    msg = "🔥 *TENDER LEADS*\n\n"

    for i, item in enumerate(new_items, 1):
        msg += f"{i}. {item['title']}\n💰 {item.get('value','N/A')}\n\n"

    telegram.send_message(msg)