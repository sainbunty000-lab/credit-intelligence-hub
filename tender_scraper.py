import os
import smtplib
import requests
from email.mime.text import MIMEText
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
# Broad list of keywords to catch every potential Working Capital client
KEYWORDS = [
    "supply", "construction", "procurement", "infrastructure", "wholesale", 
    "manufacturing", "engineering", "fabrication", "logistics", "printing", 
    "maintenance", "sanitation", "consultancy", "catering", "electrical", 
    "mechanical", "civil", "trading", "distribution", "installation", "hiring"
]

def send_telegram_alert(message):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        params = {"chat_id": chat_id, "text": message}
        try:
            response = requests.get(url, params=params)
            print(f"Telegram API Status: {response.status_code}")
        except Exception as e:
            print(f"Telegram Error: {e}")

def send_email_alert(subject, body):
    sender = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")
    if sender and password:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = sender
        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(sender, password)
                server.sendmail(sender, sender, msg.as_string())
            print("Email sent successfully.")
        except Exception as e:
            print(f"Email Error: {e}")

def run_scraper():
    print("Starting Scraper...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        url = "https://etenders.hry.nic.in/nicgep/app"
        print(f"Navigating to {url}...")
        page.goto(url, wait_until="networkidle")
        
        page.wait_for_selector('table')
        soup = BeautifulSoup(page.content(), 'html.parser')
        rows = soup.find_all('tr')
        
        matches_found = 0
        for row in rows:
            row_text = row.get_text().lower()
            
            # Check if any of our broad keywords appear in the row
            if any(key in row_text for key in KEYWORDS):
                clean_text = " ".join(row_text.split())
                alert_msg = f"🔍 CREDIT OPPORTUNITY FOUND:\n{clean_text[:200]}..."
                
                print(f"Match found: {clean_text[:50]}...")
                
                # Send notifications
                send_telegram_alert(alert_msg)
                send_email_alert("New Credit Opportunity in Haryana", alert_msg)
                matches_found += 1
        
        if matches_found == 0:
            print("No new tenders found matching your keywords today.")
        else:
            print(f"Success! Found and notified {matches_found} new opportunities.")
        
        browser.close()

if __name__ == "__main__":
    run_scraper()
