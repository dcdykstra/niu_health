import time
import datetime as dt

import pandas as pd


from config.configlog import config, logger


from scraper.pages.login import LoginPage
from scraper.pages.content import ContentPage
from scraper.pages.practice import PracticePage
from scraper.pages.reports import ReportsPage
from scraper.pages.visitsReport import VisitsReport
from scraper.pages.cptReport import CPTsReport
from scraper.pages.aptReport import AppointmentsReport

from scraper.helpers.driver import Driver
from scraper.helpers.cleaners import FileCleaner


def scrape_yesterday():
    ## Instantiate the helper class
    helper = FileCleaner()

    ## Set the directories for downloads and output
    downloads = helper.get_dir_path("downloads")

    ## Set the driver settings
    driver_settings = Driver.get_driver(downloads)
    driver = driver_settings.driver

    ## Set the dates for the report
    now = dt.datetime.now()
    yesterday = now - dt.timedelta(days=1)
    date = yesterday.strftime("%Y-%m-%d")
    yesterday = yesterday.strftime("%m-%d-%Y")

    ## Instantiate the page objects
    login = LoginPage(driver_settings)
    content = ContentPage(driver_settings)
    reports = ReportsPage(driver_settings)
    practice = PracticePage(driver_settings)
    apts = AppointmentsReport(driver_settings)
    visits = VisitsReport(driver_settings)
    cptpage = CPTsReport(driver_settings)

    ## Start the scraping process
    driver.get("https://service.emedpractice.com/index.aspx")

    ## LOGIN
    login.enter_username(config.loginid)
    login.enter_password(config.loginpassword)
    login.click_login()

    ## GET THE CURRENT CPTS
    content.nav_practice()
    practice.nav_favorites()
    practice.select_crd()
    cpts = practice.scrape_cpts()
    time.sleep(10)

    ## GET CPTs REPORT
    content.nav_reports()
    reports.load_report("cpt_bills_reportV2")
    cptpage.enter_cpt_code(",".join(cpts["code"].unique()))
    cptpage.select_search_by("R")
    cptpage.select_date_range(yesterday, yesterday)

    cptpage.click_submit()
    helper.extract_zips(downloads)

    cptpage_df = cptpage.scrape_table()
    cptpage_df.to_csv("data//downloads//cptreport.csv", index=False)

    ## GET THE APPOINTMENTS REPORT
    content.nav_reports()
    reports.load_report("AppointmentReportv1")
    apts.select_search_by("R")
    apts.select_date_range(yesterday, yesterday)

    apts.click_submit()
    helper.extract_zips(downloads)

    apts.download_csv()
    time.sleep(5)
    helper.rename_csv("AppointmentsReport.csv", "Appointment_Report", downloads)

    ## GET THE VISITS REPORT
    reports.load_report("visitreport")
    visits.stage_visits(yesterday, yesterday)

    visits.click_submit()
    helper.extract_zips(downloads)

    visits.download_csv()
    time.sleep(5)
    helper.rename_csv("VisitReport.csv", "Visit_Report", downloads)
    helper.clear_zips(downloads)

    logger.info("[ OKAY ] Completed Scrape Execution")

    driver.close()
    driver.quit()

    return date


def scrape_date(date: str):
    """date -> YYYY-MM-DD"""
    ## Instantiate the helper class
    helper = FileCleaner()

    ## Set the directories for downloads and output
    downloads = helper.get_dir_path("downloads")

    ## Set the driver settings
    driver_settings = Driver.get_driver(downloads)
    driver = driver_settings.driver

    ## Set the dates for the report
    date_parse = pd.to_datetime(date, format="%Y-%m-%d")
    date_parse = date_parse.strftime("%m-%d-%Y")

    ## Instantiate the page objects
    login = LoginPage(driver_settings)
    content = ContentPage(driver_settings)
    reports = ReportsPage(driver_settings)
    practice = PracticePage(driver_settings)
    apts = AppointmentsReport(driver_settings)
    visits = VisitsReport(driver_settings)
    cptpage = CPTsReport(driver_settings)

    ## Start the scraping process
    driver.get("https://service.emedpractice.com/index.aspx")

    ## LOGIN
    login.enter_username(config.loginid)
    login.enter_password(config.loginpassword)
    login.click_login()

    ## GET THE CURRENT CPTS
    content.nav_practice()
    practice.nav_favorites()
    practice.select_crd()
    cpts = practice.scrape_cpts()
    time.sleep(10)

    ## GET CPTs REPORT
    content.nav_reports()
    reports.load_report("cpt_bills_reportV2")
    cptpage.enter_cpt_code(",".join(cpts["code"].unique()))
    cptpage.select_search_by("R")
    cptpage.select_date_range(date_parse, date_parse)

    cptpage.click_submit()
    helper.extract_zips(downloads)

    cptpage_df = cptpage.scrape_table()
    cptpage_df.to_csv("data//downloads//cptreport.csv", index=False)

    ## GET THE APPOINTMENTS REPORT
    content.nav_reports()
    reports.load_report("AppointmentReportv1")
    apts.select_search_by("R")
    apts.select_date_range(date_parse, date_parse)

    apts.click_submit()
    helper.extract_zips(downloads)

    apts.download_csv()
    time.sleep(5)
    helper.rename_csv("AppointmentsReport.csv", "Appointment_Report", downloads)

    ## GET THE VISITS REPORT
    reports.load_report("visitreport")
    visits.stage_visits(date_parse, date_parse)

    visits.click_submit()
    helper.extract_zips(downloads)

    visits.download_csv()
    time.sleep(5)
    helper.rename_csv("VisitReport.csv", "Visit_Report", downloads)
    helper.clear_zips(downloads)

    logger.info("[ OKAY ] Completed Scrape Execution")

    driver.close()
    driver.quit()

    return date
