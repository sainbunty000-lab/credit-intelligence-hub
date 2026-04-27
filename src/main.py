from utils.logger import setup_logger
from config.settings import JOB_TYPE
from utils.error_handler import handle_error

from scrapers.tender_scraper import run_tender_scraper
from scrapers.b2b_monitor import run_b2b_monitor


logger = setup_logger("main")


def run():
    logger.info(f"🚀 Starting job: {JOB_TYPE}")

    if JOB_TYPE == "tender":
        run_tender_scraper()

    elif JOB_TYPE == "b2b":
        run_b2b_monitor()

    else:
        raise ValueError(f"❌ Invalid JOB_TYPE: {JOB_TYPE}")

    logger.info("✅ Job completed successfully")


if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        handle_error(e, context=JOB_TYPE)
        raise  # VERY IMPORTANT → ensures GitHub marks job as failed
