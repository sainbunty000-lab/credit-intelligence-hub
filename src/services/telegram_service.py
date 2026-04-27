import requests
import logging
import time
from typing import Optional

from config.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

logger = logging.getLogger(__name__)

BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


class TelegramService:
    def __init__(self):
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
            raise ValueError("❌ Telegram credentials are not set in environment variables")

    # ----------------------------
    # CORE SEND METHOD
    # ----------------------------

    def send_message(
        self,
        text: str,
        parse_mode: str = "Markdown",
        retries: int = 3,
        disable_web_page_preview: bool = False,
    ):
        """
        Send a Telegram message with retry logic
        """

        url = f"{BASE_URL}/sendMessage"

        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": disable_web_page_preview,
        }

        for attempt in range(retries):
            try:
                response = requests.post(url, json=payload, timeout=10)

                if response.status_code == 200:
                    logger.info("📬 Telegram message sent")
                    return response.json()

                else:
                    logger.warning(
                        f"⚠️ Telegram API error (attempt {attempt+1}): {response.text}"
                    )

            except requests.exceptions.RequestException as e:
                logger.warning(
                    f"⚠️ Telegram request failed (attempt {attempt+1}): {e}"
                )

            time.sleep(2 ** attempt)  # exponential backoff

        logger.error("❌ Failed to send Telegram message after retries")
        raise Exception("Telegram send_message failed")

    # ----------------------------
    # FORMATTING HELPERS
    # ----------------------------

    @staticmethod
    def format_tender(item: dict) -> str:
        """
        Format tender data into Telegram-friendly message
        Expected keys: title, source, url, value, location
        """

        title = item.get("title", "N/A")
        source = item.get("source", "N/A")
        url = item.get("url", "")
        value = item.get("value", "N/A")
        location = item.get("location", "N/A")

        message = (
            f"*{title}*\n\n"
            f"📍 Location: {location}\n"
            f"💰 Value: {value}\n"
            f"🏢 Source: {source}\n\n"
            f"[🔗 View Tender]({url})"
        )

        return message

    # ----------------------------
    # BULK SEND (OPTIONAL)
    # ----------------------------

    def send_bulk_messages(self, messages: list[str], delay: float = 1.0):
        """
        Send multiple messages with delay to avoid rate limits
        """
        for msg in messages:
            try:
                self.send_message(msg)
                time.sleep(delay)
            except Exception as e:
                logger.error(f"❌ Failed to send one message: {e}")
