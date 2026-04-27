import os


def get_env(name: str, default: str = None, required: bool = False) -> str:
    """
    Safely fetch environment variables
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
# TELEGRAM (REQUIRED)
# ----------------------------

TELEGRAM_BOT_TOKEN = get_env("TELEGRAM_BOT_TOKEN", required=True)
TELEGRAM_CHAT_ID = get_env("TELEGRAM_CHAT_ID", required=True)


# ----------------------------
# APP CONFIG
# ----------------------------

JOB_TYPE = get_env("JOB_TYPE", default="tender")  # tender | b2b
ENVIRONMENT = get_env("ENVIRONMENT", default="production")
LOG_LEVEL = get_env("LOG_LEVEL", default="INFO")
