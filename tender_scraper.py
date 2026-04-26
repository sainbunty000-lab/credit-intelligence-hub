import os
import smtplib
import requests
from email.mime.text import MIMEText
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# --- CONFIGURATION & ALERTS ---
def send_telegram_alert(message):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}"
        requests.get(url)

def send_email_alert(subject, body):
    sender = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")
    if sender and password:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = sender
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender, password)
            server.sendmail(sender, sender, msg.as_string())

# --- SCRAPER LOGIC ---
def run_scraper():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        url = "https://etenders.hry.nic.in/nicgep/app"
        print(f"Navigating to {url}...")
        page.goto(url, wait_until="networkidle")
        
        # Wait for the table element to ensure page is loaded
        page.wait_for_selector('table')
        
        # Parse content
        soup = BeautifulSoup(page.content(), 'html.parser')
        rows = soup.find_all('tr')
        
        # Keywords that indicate working capital needs
        keywords = ["supply", "construction", "procurement", "wholesale", "infrastructure"]
        
        matches_found = 0
        for row in rows:
            text = row.get_text().lower()
            if any(key in text for key in keywords):
                # Clean up the text for the notification
                clean_text = " ".join(text.split())
                alert_msg = f"🔍 CREDIT OPPORTUNITY FOUND:\n{clean_text[:200]}..."
                
                print(f"Match found: {clean_text[:50]}...")
                
                # Trigger Alerts
                send_telegram_alert(alert_msg)
                send_email_alert("New Credit Opportunity in Haryana", alert_msg)
                matches_found += 1
        
        print(f"Scrape complete. Found {matches_found} new opportunities.")
        browser.close()

if __name__ == "__main__":
    run_scraper()

