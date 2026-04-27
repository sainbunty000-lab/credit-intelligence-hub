import google.auth
from google.auth.transport.requests import Request

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_gcp_credentials():
    creds, _ = google.auth.default(scopes=SCOPES)

    if creds.requires_scopes:
        creds = creds.with_scopes(SCOPES)

    if not creds.valid:
        creds.refresh(Request())

    return creds
