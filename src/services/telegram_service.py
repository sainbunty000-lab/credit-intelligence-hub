import requests
import os


class TelegramService:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")

    def send_message(self, text: str):
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"

        # split long messages
        chunks = [text[i:i+3500] for i in range(0, len(text), 3500)]

        for chunk in chunks:
            requests.post(url, data={
                "chat_id": self.chat_id,
                "text": chunk,
                "parse_mode": "Markdown"
            })
