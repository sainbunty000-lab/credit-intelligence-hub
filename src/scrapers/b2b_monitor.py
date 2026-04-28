from services.telegram_service import TelegramService


def run_b2b_monitor():
    telegram = TelegramService()

    leads = [
        "Need supplier for Gurgaon project (3 Cr)",
        "Urgent bulk order requirement Haryana"
    ]

    msg = "📦 *B2B LEADS*\n\n"

    for i, item in enumerate(leads, 1):
        msg += f"{i}. {item}\n\n"

    telegram.send_message(msg)
