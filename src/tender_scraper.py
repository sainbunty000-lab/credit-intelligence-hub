import os
import requests
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from sheets_helper import log_to_sheets

def send_telegram_alert(message):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        params = {"chat_id": chat_id, "text": message}
        try:
            requests.get(url, params=params)
        except Exception as e:
            print(f"Telegram Error: {e}")

def run_scraper():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://etenders.hry.nic.in/nicgep/app", wait_until="networkidle")
        page.wait_for_timeout(5000)
        
        soup = BeautifulSoup(page.content(), 'html.parser')
        rows = soup.find_all('tr')
        
        for row in rows:
            row_text = row.get_text().lower()
            if any(k in row_text for k in ["supply", "construction", "procurement"]):
                alert_msg = f"🔍 TENDER LEAD:\n{row_text[:150]}"
                
                # 1. Notify
                send_telegram_alert(alert_msg)
                
                # 2. Log to CRM
                try:
                    log_to_sheets(row_text[:50], "Tender Lead", "https://etenders.hry.nic.in/nicgep/app")
                except Exception as e:
                    print(f"Sheet Logging Error: {e}")
                    
        browser.close()

if __name__ == "__main__":
    run_scraper()
