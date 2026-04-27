import gspread
from google.auth import default

def get_sheet(sheet_name="Lead_Tracker"):
    try:
        creds, _ = default()
        client = gspread.authorize(creds)
        return client.open(sheet_name).sheet1
    except Exception as e:
        print(f"Connection Failed: {e}. Please ensure the sheet '{sheet_name}' is shared with your Service Account email.")
        raise

def add_lead(sheet, lead_data):
    try:
        sheet.append_row(lead_data)
        return True
    except Exception as e:
        print(f"Update Error: {e}")
        return False
