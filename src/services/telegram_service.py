import importlib

try:
    requests = importlib.import_module("requests")
except Exception:  # requests may not be installed in some environments
    requests = None

import logging
import time
from typing import List, Optional
import json
import urllib.request
import urllib.error

from config.settings import (
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_TENDER_CHAT_ID,
    TELEGRAM_B2B_CHAT_ID,
    JOB_TYPE,
    DRY_RUN,
)

logger = logging.getLogger(__name__)


class TelegramService:
    def __init__(self, chat_id: Optional[str] = None):
        if not TELEGRAM_BOT_TOKEN:
            raise ValueError("❌ Missing TELEGRAM_BOT_TOKEN")

        # Auto-route chat based on job
        if chat_id:
            self.chat_id = chat_id
        else:
            self.chat_id = self._resolve_chat_id()

        if not self.chat_id:
            raise ValueError("❌ No Telegram chat_id configured")

        self.base_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

    # ----------------------------
    # CHAT ROUTING
    # ----------------------------

    def _resolve_chat_id(self) -> str:
        if JOB_TYPE == "tender":
            return TELEGRAM_TENDER_CHAT_ID
        elif JOB_TYPE == "b2b":
            return TELEGRAM_B2B_CHAT_ID
        else:
            return None

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

        if DRY_RUN:
            logger.info(f"[DRY_RUN] Telegram message:\n{text}")
            return

        url = f"{self.base_url}/sendMessage"

        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": disable_web_page_preview,
        }

        for attempt in range(retries):
            try:
                if requests is not None:
                    response = requests.post(url, json=payload, timeout=10)

                    if getattr(response, "status_code", None) == 200:
                        logger.info("📬 Telegram message sent")
                        return response.json()

                    else:
                        logger.warning(
                            f"⚠️ Telegram API error (attempt {attempt+1}): {getattr(response, 'text', '')}"
                        )
                else:
                    # Fallback to urllib if requests is not available
                    data = json.dumps(payload).encode("utf-8")
                    req = urllib.request.Request(
                        url, data=data, headers={"Content-Type": "application/json"}
                    )
                    try:
                        with urllib.request.urlopen(req, timeout=10) as resp:
                            resp_text = resp.read().decode("utf-8")
                            logger.info("📬 Telegram message sent")
                            try:
                                return json.loads(resp_text)
                            except Exception:
                                return {"raw": resp_text}
                    except urllib.error.HTTPError as e:
                        try:
                            resp_text = e.read().decode("utf-8")
                        except Exception:
                            resp_text = str(e)
                        logger.warning(
                            f"⚠️ Telegram API error (attempt {attempt+1}): {resp_text}"
                        )

            except Exception as e:
                logger.warning(
                    f"⚠️ Telegram request failed (attempt {attempt+1}): {e}"
                )

            time.sleep(2 ** attempt)

        logger.error("❌ Failed to send Telegram message after retries")
        raise Exception("Telegram send_message failed")

    # ----------------------------
    # SAFE FORMATTING
    # ----------------------------

    @staticmethod
    def escape_markdown(text: str) -> str:
        """
        Escape Telegram Markdown special characters
        """
        escape_chars = r"_*[]()~`>#+-=|{}.!"
        return "".join(f"\\{c}" if c in escape_chars else c for c in text)

    # ----------------------------
    # FORMATTING HELPERS
    # ----------------------------

    def format_tender(self, item: dict) -> str:
        title = self.escape_markdown(item.get("title", "N/A"))
        source = self.escape_markdown(item.get("source", "N/A"))
        url = item.get("url", "")
        value = self.escape_markdown(item.get("value", "N/A"))
        location = self.escape_markdown(item.get("location", "N/A"))

        return (
            f"*{title}*\n\n"
            f"📍 Location: {location}\n"
            f"💰 Value: {value}\n"
            f"🏢 Source: {source}\n\n"
            f"[🔗 View Tender]({url})"
        )

    def format_b2b(self, item: dict) -> str:
        title = self.escape_markdown(item.get("title", "N/A"))
        source = self.escape_markdown(item.get("source", "N/A"))
        url = item.get("url", "")
        value = self.escape_markdown(item.get("value", "N/A"))
        location = self.escape_markdown(item.get("location", "N/A"))

        return (
            f"*{title}*\n\n"
            f"📍 Location: {location}\n"
            f"💰 Value: {value}\n"
            f"🏢 Source: {source}\n\n"
            f"[🔗 View Lead]({url})"
        )

    # ----------------------------
    # BULK SEND
    # ----------------------------

    def send_bulk_messages(self, messages: List[str], delay: float = 1.0):
        for msg in messages:
            try:
                self.send_message(msg)
                time.sleep(delay)
            except Exception as e:
                logger.error(f"❌ Failed to send one message: {e}")
