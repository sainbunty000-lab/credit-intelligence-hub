import os
import gspread
import requests
from google.auth import default

# 1. Setup Google Sheets Authentication (Uses Workload Identity automatically)
creds, _ = default()
client = gspread.authorize(creds)
sheet = client.open("Lead_Tracker").sheet1

# 2. Setup Telegram details
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, json=payload)

def main():
    print("Starting Tender Scraper...")
    
    # --- YOUR SCRAPING LOGIC GOES HERE ---
    # Example: leads = scrape_site_logic()
    leads = [{"id": "T123", "details": "Sample Tender"}] 
    
    # --- UPDATE SHEET ---
    for lead in leads:
        sheet.append_row([lead['id'], lead['details']])
        send_telegram(f"New Tender Found: {lead['details']}")
        print(f"Added {lead['id']} to sheet.")

if __name__ == "__main__":
    main()
