from scrapers.tender_scraper import run_tender_scraper
from scrapers.b2b_monitor import run_b2b_monitor
import os


def run():
    job = os.getenv("JOB_TYPE", "tender")

    if job == "tender":
        run_tender_scraper()
    elif job == "b2b":
        run_b2b_monitor()
    else:
        raise ValueError("Invalid JOB_TYPE")


if __name__ == "__main__":
    run()
