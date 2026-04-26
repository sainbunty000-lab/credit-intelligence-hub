from playwright.sync_api import sync_playwright

def run_scraper():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Navigate to Haryana e-Tender portal
        url = "https://etenders.hry.nic.in/nicgep/app"
        print(f"Navigating to {url}...")
        
        page.goto(url, wait_until="networkidle")
        print(f"Successfully accessed: {page.title()}")
        
        browser.close()

if __name__ == "__main__":
    run_scraper()
