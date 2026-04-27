import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def log_to_sheets(lead_name, industry, source):
    # Load credentials from GitHub Secret
    creds_dict = json.loads(os.getenv('GOOGLE_SHEETS_CREDENTIALS'))
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    
    # Open sheet and append row
    sheet = client.open("Lead_Tracker").sheet1
    sheet.append_row(["2026-04-27", lead_name, industry, "New Lead", source])
