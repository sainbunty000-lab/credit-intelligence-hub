from playwright.sync_api import sync_playwright
from services.telegram_service import TelegramService


def scrape():
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto("https://bidplus.gem.gov.in/all-bids")
        page.wait_for_timeout(5000)

        rows = page.query_selector_all("table tbody tr")

        for row in rows[:5]:
            cols = row.query_selector_all("td")
            if len(cols) < 5:
                continue

            title = cols[1].inner_text()
            value = cols[4].inner_text()

            results.append(f"{title}\n💰 {value}")

        browser.close()

    return results


def run_tender_scraper():
    telegram = TelegramService()

    items = scrape()

    if not items:
        return

    msg = "🔥 *TENDER LEADS*\n\n"

    for i, item in enumerate(items, 1):
        msg += f"{i}. {item}\n\n"

    telegram.send_message(msg)
