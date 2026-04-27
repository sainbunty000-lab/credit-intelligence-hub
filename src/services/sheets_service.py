import time
import logging
from typing import List

import gspread
from google.auth.transport.requests import Request

from auth.gcp_auth import get_gcp_credentials
from config.settings import SHEET_NAME

logger = logging.getLogger(__name__)


class SheetsService:
    def __init__(self):
        self.enabled = False
        self.client = None
        self.sheet = None

        try:
            creds = get_gcp_credentials()

            if not creds.valid:
                creds.refresh(Request())

            self.client = gspread.authorize(creds)
            self.sheet = self.client.open(SHEET_NAME or "Lead_Tracker").sheet1

            self.enabled = True
            logger.info("✅ Google Sheets connected")

        except Exception as e:
            logger.warning(f"⚠️ Sheets disabled (local mode): {e}")

    # ----------------------------
    # WRITE
    # ----------------------------

    def append_rows(self, rows: List[List[str]]):
        if not rows:
            return

        if not self.enabled:
            print("\n📊 LOCAL OUTPUT:")
            for r in rows:
                print(r)
            print("\n")
            return

        for i in range(3):
            try:
                self.sheet.append_rows(rows, value_input_option="USER_ENTERED")
                return
            except Exception as e:
                logger.warning(f"Retry {i+1}: {e}")
                time.sleep(2 ** i)

    # ----------------------------
    # READ
    # ----------------------------

    def get_existing_ids(self, col_index: int = 1):
        if not self.enabled:
            return set()

        try:
            values = self.sheet.col_values(col_index)
            return set(values[1:])
        except:
            return set()