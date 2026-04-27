import os
import gspread
import requests
from google.auth import default

# Initialize Auth
creds, _ = default()
client = gspread.authorize(creds)
sheet = client.open("Lead_Tracker").sheet1

# Run Logic
def main():
    print("Bot starting...")
    # Add your scraping logic here
    print("Scraping complete.")

if __name__ == "__main__":
    main()
