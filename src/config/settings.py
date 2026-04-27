import os


def get_env(name: str, default: str = None, required: bool = False) -> str:
    """
    Safely fetch environment variables with validation
    """
    value = os.getenv(name, default)

    if required and not value:
        raise ValueError(f"❌ Missing required environment variable: {name}")

    return value


# ----------------------------
# GOOGLE SHEETS
# ----------------------------

SHEET_NAME = get_env("SHEET_NAME", default="Lead_Tracker")


# ----------------------------
# TELEGRAM (CORE)
# ----------------------------

TELEGRAM_BOT_TOKEN = get_env("TELEGRAM_BOT_TOKEN", required=True)

# Default fallback (for backward compatibility)
TELEGRAM_CHAT_ID = get_env("TELEGRAM_CHAT_ID", default=None)

# New: Per-job channels
TELEGRAM_TENDER_CHAT_ID = get_env("TELEGRAM_TENDER_CHAT_ID", default=TELEGRAM_CHAT_ID)
TELEGRAM_B2B_CHAT_ID = get_env("TELEGRAM_B2B_CHAT_ID", default=TELEGRAM_CHAT_ID)


# ----------------------------
# APP CONFIG
# ----------------------------

JOB_TYPE = get_env("JOB_TYPE", default="tender")  # tender | b2b
ENVIRONMENT = get_env("ENVIRONMENT", default="production")
LOG_LEVEL = get_env("LOG_LEVEL", default="INFO")


# ----------------------------
# SCRAPER CONFIG
# ----------------------------

MAX_RETRIES = int(get_env("MAX_RETRIES", default="3"))
REQUEST_TIMEOUT = int(get_env("REQUEST_TIMEOUT", default="10"))

# Parallel scraping
MAX_WORKERS = int(get_env("MAX_WORKERS", default="3"))


# ----------------------------
# FILTERING CONFIG
# ----------------------------

ENABLE_PRIORITY_FILTER = get_env("ENABLE_PRIORITY_FILTER", default="true").lower() == "true"
PRIORITY_THRESHOLD = int(get_env("PRIORITY_THRESHOLD", default="2"))


# ----------------------------
# DEBUG / DEV FLAGS
# ----------------------------

DRY_RUN = get_env("DRY_RUN", default="false").lower() == "true"
