import hashlib
from datetime import datetime

from playwright.sync_api import sync_playwright

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
# SCRAPER (IndiaMART STYLE)
# ----------------------------
def scrape_b2b_sources():
    results = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            logger.info("🌐 Opening B2B source")

            # Example search (you can refine later)
            page.goto("https://dir.indiamart.com/search.mp?ss=construction", timeout=60000)

            page.wait_for_timeout(5000)

            items = page.query_selector_all(".cardbody")

            for item in items[:15]:
                try:
                    title_el = item.query_selector("a")

                    if not title_el:
                        continue

                    title = title_el.inner_text().strip()
                    url = title_el.get_attribute("href")

                    results.append({
                        "title": title,
                        "source": "IndiaMART",
                        "url": url or "https://dir.indiamart.com",
                        "location": "",  # often not directly available
                        "value": "",     # B2B rarely shows value
                        "description": title,
                    })

                except Exception:
                    continue

            browser.close()

    except Exception as e:
        logger.error(f"❌ B2B scraping failed: {e}")

    logger.info(f"📊 Scraped {len(results)} B2B items")

    return results


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
    # TEMP TEST (IMPORTANT)
    # ----------------------------
    # Uncomment this for first run if nothing passes filter
    # filtered_items = items

    # ----------------------------
    # Funding Filter
    # ----------------------------
    filtered_items = items  # 🔥 TEMP DEBUG MODE

    if not filtered_items:
        logger.info("❌ No funding opportunities (B2B)")
        return

    # ----------------------------
    # Scoring
    # ----------------------------
    for item in filtered_items:
        item["score"] = score_lead(item)

    # Sort by score
    filtered_items = sorted(filtered_items, key=lambda x: x["score"], reverse=True)

    # Take TOP 3
    top_items = filtered_items[:3]

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
            f"📦 Demand Signal\n"
            f"📍 {item.get('location','N/A')}\n\n"
        )

    message += "👉 Action: Reach out for working capital discussion"

    telegram.send_message(message)

    logger.info(f"✅ {len(new_items)} B2B leads sent")
