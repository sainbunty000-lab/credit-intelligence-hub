import traceback
from services.telegram_service import TelegramService
from utils.logger import setup_logger

logger = setup_logger("error_handler")


def handle_error(e: Exception, context: str = "Unknown Job"):
    """
    Global error handler:
    - Logs error
    - Sends Telegram alert
    """

    telegram = TelegramService()

    error_trace = traceback.format_exc()

    logger.error(f"❌ Error in {context}: {str(e)}")
    logger.error(error_trace)

    message = (
        f"🚨 *SCRAPER FAILURE ALERT*\n\n"
        f"📌 Job: {context}\n"
        f"❌ Error: `{str(e)}`\n\n"
        f"🧾 Traceback:\n"
        f"```{error_trace[:3000]}```"  # Telegram limit safe
    )

    try:
        telegram.send_message(message, parse_mode="Markdown")
    except Exception as telegram_error:
        logger.error(f"❌ Failed to send Telegram alert: {telegram_error}")
