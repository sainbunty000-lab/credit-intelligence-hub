import os
import requests
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from sheets_helper import log_to_sheets

def send_telegram_alert(message):
    token = os.getenv("B2B_BOT_TOKEN") 
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        params = {"chat_id": chat_id, "text": message}
        try:
            requests.get(url, params=params)
        except Exception as e:
            print(f"Telegram Error: {e}")

def run_b2b_monitor():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://dir.indiamart.com/impcat/electronic-components.html?city=gurugram", wait_until="networkidle")
        
        soup = BeautifulSoup(page.content(), 'html.parser')
        
        for name in soup.select('.cmp-name'):
            if "verified" in name.get_text().lower():
                trader_name = name.get_text().strip()
                alert_msg = f"💎 HIGH-VALUE TRADER:\n{trader_name}"
                
                # 1. Notify via Telegram
                send_telegram_alert(alert_msg)
                
                # 2. Log to CRM
                try:
                    log_to_sheets(trader_name, "B2B Trader", "https://dir.indiamart.com/impcat/electronic-components.html?city=gurugram")
                except Exception as e:
                    print(f"Sheet Logging Error: {e}")
        
        browser.close()

if __name__ == "__main__":
    run_b2b_monitor()
