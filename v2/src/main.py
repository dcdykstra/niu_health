import pandas as pd
import datetime as dt

from scraper.scrape import scrape_yesterday, scrape_date
from transform.transform import (
    parse_appointments,
    parse_cpts,
    parse_visitors,
    merge_daily_report,
)
from load.gdriveupload import upload_files

if __name__ == "__main__":
    # date = scrape_date("2024-07-19")
    date = scrape_yesterday()
    apt_df = parse_appointments()
    cpt_df = parse_cpts()
    vis_df = parse_visitors()

    final = merge_daily_report(apt_df, cpt_df, vis_df)
    final.to_excel(f"data/output/detainee_list_{date}.xlsx", index=False)

    upload_files([f"data/output/detainee_list_{date}.xlsx"])
