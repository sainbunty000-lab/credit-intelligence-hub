import os
import requests
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def send_telegram_alert(message):
    # Uses your NEW B2B_BOT_TOKEN
    token = os.getenv("B2B_BOT_TOKEN") 
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        params = {"chat_id": chat_id, "text": message}
        requests.get(url, params=params)

def run_b2b_monitor():
    send_telegram_alert("🚀 B2B Trade Monitor: Scan started.")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        # Example URL for verified traders
        page.goto("https://dir.indiamart.com/impcat/electronic-components.html?city=gurugram", wait_until="networkidle")
        
        soup = BeautifulSoup(page.content(), 'html.parser')
        # Logic to find verified traders
        for name in soup.select('.cmp-name'):
            if "Verified" in name.get_text():
                send_telegram_alert(f"💎 HIGH-VALUE TRADER:\n{name.get_text().strip()}")
        browser.close()

if __name__ == "__main__":
    run_b2b_monitor()
