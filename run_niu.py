import configparser
import unittest
import time
import os

from classes import *
from niu import NIU
from xlsx_writer_niu import XLSX
from cpt_report import CPTs_Report_Page
from log import logger

from datetime import date, timedelta
from configparser import ConfigParser
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

class RunTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.prefs = {'profile.default_content_setting_values.automatic_downloads': 1}
        cls.options = webdriver.ChromeOptions()
        # cls.options.add_argument('--headless')
        cls.options.add_argument('--disable-dev-shm-usage')
        cls.options.add_argument('--ignore-certificate-errors')
        cls.options.add_argument('--ignore-ssl-errors')
        cls.options.add_experimental_option('excludeSwitches', ['enable-logging'])
        cls.options.add_experimental_option('prefs', cls.prefs)
        cls.driver = webdriver.Chrome(service = Service(ChromeDriverManager().install()), options=cls.options)
        cls.actions = ActionChains(cls.driver)
        cls.wait = WebDriverWait(cls.driver, 20)

    def test_detainee(self):
        path = os.path.dirname(os.path.abspath(__file__))
        config = ConfigParser()

        config.read(f"{path}\\config.ini")
        userinfo = config["USERINFO"]

        driver = self.driver
        wait = self.wait

        login = LoginPage(driver, wait)
        report = ReportPage(driver, wait)
        niu = NIU(driver, wait)

        # Set date to previous date
        # Necessary if fully automating and using a task scheduler
        day = date.today() - timedelta(days=1)
        day = day.strftime("%m-%d-%Y")

        # Login
        driver.get("https://service.emedpractice.com/index.aspx")
        login.enter_username(userinfo["loginid"])
        login.enter_password(userinfo["password"])
        login.click_login()

        # Go to report page
        report.nav_reports()
        logger.info(f"Starting Date {day}")

        # Load, stage, and scrape Appointments Report
        report.load_report("AppointmentReportv1")
        niu.stage_apt(day, day)
        apt = niu.scrape_table("_ctl0_ContentPlaceHolder1_gvAppointments")

        # Load, stage, and scrape Patient Visit Report
        report.load_report("visitreport")
        niu.stage_pt(day, day)
        visit = niu.scrape_table("_ctl0_ContentPlaceHolder1_gvCount")

        # Load, stage, and scrape CPT Codes Report
        report.load_report("cpt_bills_reportV2")
        niu.stage_cpt(day, day)
        cpt = niu.scrape_table("_ctl0_ContentPlaceHolder1_gvreport")

        # Generate data for XLSX pages
        p1 = niu.gen_final(visit, apt, cpt, page = 1)
        p2 = niu.gen_final(cpt, visit, apt, page = 2)

        # Write data into XLSX workbook
        xlsx = XLSX(day)
        xlsx.write_report(p1, p2)

        time.sleep(2)
        logger.info("Completed Execution")

    @classmethod
    def tearDownClass(cls):
        cls.driver.close()
        cls.driver.quit()
        print("Driver Closed")

if __name__ == '__main__':
    unittest.main()