import gspread
from google.auth import default

def get_sheet(sheet_name="Lead_Tracker"):
    # This automatically finds the credentials provided by the GitHub Action
    creds, _ = default()
    client = gspread.authorize(creds)
    return client.open(sheet_name).sheet1

def add_lead(sheet, lead_data):
    try:
        sheet.append_row(lead_data)
        return True
    except Exception as e:
        print(f"Error adding lead: {e}")
        return False
