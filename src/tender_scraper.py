import os
import gspread
import requests
from google.auth import default
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
KEYWORDS = ["supply", "construction", "procurement", "infrastructure", "wholesale", 
            "manufacturing", "engineering", "fabrication", "logistics", "printing", 
            "maintenance", "sanitation", "consultancy", "catering", "electrical", 
            "mechanical", "civil", "trading", "distribution", "installation", "hiring"]

# 1. Auth Setup
creds, _ = default()
client = gspread.authorize(creds)
sheet = client.open("Lead_Tracker").sheet1

def send_telegram_alert(message):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        # Using POST with JSON is safer than GET
        payload = {"chat_id": chat_id, "text": message}
        requests.post(url, json=payload)

def run_scraper():
    print("Starting Scraper...")
    existing_ids = sheet.col_values(1) # To prevent duplicates
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # NOTE: You may need to navigate to the specific "Active Tenders" page
        # Example: page.goto("https://etenders.hry.nic.in/nicgep/app?component=%24DirectLink&page=FrontEndActiveTenders&service=direct&session=T")
        url = "https://etenders.hry.nic.in/nicgep/app"
        page.goto(url, wait_until="networkidle")
        
        # If there is a click needed, add it here:
        # page.click("text=Active Tenders") 
        
        soup = BeautifulSoup(page.content(), 'html.parser')
        rows = soup.find_all('tr')
        
        for row in rows:
            row_text = row.get_text().lower()
            if any(key in row_text for key in KEYWORDS):
                # Extract a unique ID (assuming first cell is the ID)
                cells = row.find_all('td')
                if len(cells) > 0:
                    tender_id = cells[0].text.strip()
                    
                    if tender_id not in existing_ids:
                        clean_text = " ".join(row_text.split())
                        
                        # Save to Sheet
                        sheet.append_row([tender_id, clean_text[:200]])
                        
                        # Alert Telegram
                        alert_msg = f"🔍 CREDIT OPPORTUNITY:\n{clean_text[:200]}..."
                        send_telegram_alert(alert_msg)
                        
                        existing_ids.append(tender_id)
        
        browser.close()

if __name__ == "__main__":
    run_scraper()
