import os
import smtplib
import requests
from email.mime.text import MIMEText
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
KEYWORDS = ["supply", "construction", "procurement", "infrastructure", "wholesale", 
            "manufacturing", "engineering", "fabrication", "logistics", "printing", 
            "maintenance", "sanitation", "consultancy", "catering", "electrical", 
            "mechanical", "civil", "trading", "distribution", "installation", "hiring"]

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
    print("Starting Scraper...")
    
    # 1. HEARTBEAT: This proves your bot and secrets are working!
    send_telegram_alert("✅ Credit Intelligence Hub: Scan has started.")

    with sync_playwright() as p:
        # 2. BROWSER FIX: Adding a User-Agent so the gov portal doesn't block you
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        page = context.new_page()
        
        url = "https://etenders.hry.nic.in/nicgep/app"
        print(f"Navigating to {url}...")
        page.goto(url, wait_until="networkidle")
        
        # Give it a second to load the dynamic content
        page.wait_for_timeout(5000) 
        
        soup = BeautifulSoup(page.content(), 'html.parser')
        rows = soup.find_all('tr')
        
        # 3. DEBUGGING: Print how many rows were found
        print(f"Found {len(rows)} rows on the page.")
        
        matches_found = 0
        for row in rows:
            row_text = row.get_text().lower()
            
            if any(key in row_text for key in KEYWORDS):
                clean_text = " ".join(row_text.split())
                alert_msg = f"🔍 CREDIT OPPORTUNITY FOUND:\n{clean_text[:200]}..."
                
                print(f"MATCH FOUND: {clean_text[:50]}")
                send_telegram_alert(alert_msg)
                matches_found += 1
        
        if matches_found == 0:
            print("No matches found today.")
            # Optional: uncomment the line below to get a 'finished' ping
            # send_telegram_alert("ℹ️ Scan complete. No new tenders matching keywords found.")
        
        browser.close()

if __name__ == "__main__":
    run_scraper()
