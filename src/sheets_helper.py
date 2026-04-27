import gspread
from google.auth import default

def get_sheet(sheet_name="Lead_Tracker"):
    """Connects to Google Sheets using your GitHub Action credentials."""
    # This automatically detects the credentials from your Workload Identity setup
    creds, _ = default()
    client = gspread.authorize(creds)
    return client.open(sheet_name).sheet1

def add_lead(sheet, lead_data):
    """Appends a new lead row to the sheet."""
    try:
        # data should be a list, e.g., ['2026-04-27', 'Company Name', 'Industry', 'New Lead']
        sheet.append_row(lead_data)
        return True
    except Exception as e:
        print(f"Error adding lead: {e}")
        return False
