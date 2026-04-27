import os
import gspread
import requests
from google.auth import default
from playwright.sync_api import sync_playwright

# 1. Setup Auth
creds, _ = default()
client = gspread.authorize(creds)
sheet = client.open("Lead_Tracker").sheet1

# 2. Telegram Helper
def send_telegram(message):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": message})

# 3. Duplicate Prevention
def get_existing_ids():
    # Gets all values from the first column (assuming it's a unique ID)
    return sheet.col_values(1) 

def main():
    print("Scraping starting...")
    existing_tenders = get_existing_ids()
    new_tenders_found = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True) # Runs in background
        page = browser.new_page()
        
        # --- REPLACE THIS URL WITH YOUR TARGET SITE ---
        page.goto("https://YOUR_TARGET_WEBSITE_HERE.com")
        
        # --- YOUR SCRAPING LOGIC HERE ---
        # Example: tender_id = page.inner_text('.tender-id-selector')
        # Example: title = page.inner_text('.title-selector')
        
        # dummy logic for testing structure:
        tender_id = "TENDER-101" 
        title = "Sample Construction Tender"

        # Check if new
        if tender_id not in existing_tenders:
            new_tenders_found.append([tender_id, title])
            sheet.append_row([tender_id, title])
            send_telegram(f"📢 New Tender: {title}")
            print(f"Added {tender_id}")
        
        browser.close()
    
    if not new_tenders_found:
        print("No new tenders found today.")

if __name__ == "__main__":
    main()
