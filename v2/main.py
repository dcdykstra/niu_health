import pandas as pd
import datetime as dt

from src.scraper.scrape import scrape_yesterday, scrape_date, scrape_date_range
from src.transform.transform import (
    parse_appointments,
    parse_cpts,
    parse_visitors,
    merge_daily_report,
)
from src.load.gdriveupload import upload_files


def lambda_handler(event, context):
    date = scrape_yesterday()
    # date = scrape_date("2024-08-03")
    apt_df = parse_appointments()
    cpt_df = parse_cpts()
    vis_df = parse_visitors()
    print("[ OK ] Scrape Complete")

    final = merge_daily_report(apt_df, cpt_df, vis_df)
    final.to_excel(f"data/output/detainee_list_{date}.xlsx", index=False)

    upload_files([f"data/output/detainee_list_{date}.xlsx"])
    print("[ SUCCESS ]")


if __name__ == "__main__":
    lambda_handler(event=None, context=None)
