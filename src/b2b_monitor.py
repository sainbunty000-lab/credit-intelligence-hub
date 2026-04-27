import os
import gspread
import requests
from google.auth import default
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
# Monitor for these specific B2B trade keywords
KEYWORDS = ["tender", "bulk", "wholesale", "import", "export", "distributor"]

# 1. Auth Setup (Matches your tender_scraper)
creds, _ = default()
client = gspread.authorize(creds)
sheet = client.open("Lead_Tracker").sheet1

def send_telegram_alert(message):
    token = os.getenv("B2B_BOT_TOKEN") # Using your B2B Bot Token
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message}
        requests.post(url, json=payload)

def run_monitor():
    print("Starting B2B Monitor...")
    existing_ids = sheet.col_values(1)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # --- B2B TARGET URL ---
        # Update this to your target B2B portal (e.g., IndiaMART, TradeIndia search)
        url = "https://YOUR_B2B_PORTAL_URL_HERE"
        page.goto(url, wait_until="networkidle")
        
        soup = BeautifulSoup(page.content(), 'html.parser')
        
        # --- SEARCH LOGIC ---
        # Looks for items/divs that match your keywords
        items = soup.select(".product-card") # Change this to the specific CSS class
        
        for item in items:
            text = item.get_text().lower()
            if any(key in text for key in KEYWORDS):
                # Using a generic ID (or title) for the monitor
                identifier = item.select_one("a")['href'] if item.select_one("a") else text[:20]
                
                if identifier not in existing_ids:
                    # Save to Sheet (Adding a label 'B2B' to distinguish from Tenders)
                    sheet.append_row(["B2B", identifier, text[:150]])
                    
                    # Notify
                    send_telegram_alert(f"🏢 New B2B Lead:\n{text[:150]}...")
                    
                    existing_ids.append(identifier)
                    print(f"New lead found: {identifier}")
        
        browser.close()

if __name__ == "__main__":
    run_monitor()
