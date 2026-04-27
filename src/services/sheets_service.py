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
        self.client = self._init_client()
        self.sheet = self._open_sheet()

    def _init_client(self):
        """Initialize gspread client using Workload Identity credentials"""
        try:
            creds = get_gcp_credentials()

            # Ensure token is valid
            if not creds.valid:
                creds.refresh(Request())

            client = gspread.authorize(creds)
            logger.info("✅ Google Sheets client initialized")
            return client

        except Exception as e:
            logger.error(f"❌ Failed to initialize Sheets client: {e}")
            raise

    def _open_sheet(self):
        """Open the target Google Sheet"""
        try:
            sheet_name = SHEET_NAME or "Lead_Tracker"
            sheet = self.client.open(sheet_name).sheet1
            logger.info(f"📊 Connected to sheet: {sheet_name}")
            return sheet

        except Exception as e:
            logger.error(f"❌ Failed to open sheet: {e}")
            raise

    # ----------------------------
    # WRITE OPERATIONS
    # ----------------------------

    def append_row(self, row: List[str], retries: int = 3):
        """Append a single row with retry logic"""
        for attempt in range(retries):
            try:
                self.sheet.append_row(row, value_input_option="USER_ENTERED")
                logger.info("✅ Row appended successfully")
                return
            except Exception as e:
                logger.warning(f"⚠️ Append row failed (attempt {attempt+1}): {e}")
                time.sleep(2 ** attempt)

        logger.error("❌ Failed to append row after retries")
        raise Exception("Append row failed")

    def append_rows(self, rows: List[List[str]], retries: int = 3):
        """Append multiple rows efficiently"""
        if not rows:
            logger.info("⚠️ No rows to append")
            return

        for attempt in range(retries):
            try:
                self.sheet.append_rows(rows, value_input_option="USER_ENTERED")
                logger.info(f"✅ {len(rows)} rows appended successfully")
                return
            except Exception as e:
                logger.warning(f"⚠️ Append rows failed (attempt {attempt+1}): {e}")
                time.sleep(2 ** attempt)

        logger.error("❌ Failed to append rows after retries")
        raise Exception("Append rows failed")

    # ----------------------------
    # READ OPERATIONS
    # ----------------------------

    def get_all_records(self):
        """Fetch all records as list of dicts"""
        try:
            records = self.sheet.get_all_records()
            logger.info(f"📥 Retrieved {len(records)} records")
            return records
        except Exception as e:
            logger.error(f"❌ Failed to fetch records: {e}")
            raise

    def get_column_values(self, col_index: int):
        """Fetch all values from a specific column"""
        try:
            values = self.sheet.col_values(col_index)
            logger.info(f"📥 Retrieved {len(values)} values from column {col_index}")
            return values
        except Exception as e:
            logger.error(f"❌ Failed to fetch column values: {e}")
            raise

    # ----------------------------
    # DEDUP SUPPORT
    # ----------------------------

    def get_existing_ids(self, col_index: int = 1):
        """
        Fetch existing IDs (for deduplication)
        Default: column 1
        """
        try:
            values = self.sheet.col_values(col_index)
            existing_ids = set(values[1:])  # skip header
            logger.info(f"🔍 Loaded {len(existing_ids)} existing IDs")
            return existing_ids
        except Exception as e:
            logger.error(f"❌ Failed to fetch existing IDs: {e}")
            raise
