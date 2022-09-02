"""
Main Script to run everything
"""
import unittest
import time

from datetime import date, timedelta
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from classes import LoginPage, ReportPage
from niu import NIU
from xlsx_writer_niu import XLSX
from configlog import config, logger, day
from googledriveupload import upload_xlsx


class RunTest(unittest.TestCase):
    """Wrap in Tests to empty anything used to not need garbage collection"""
    @classmethod
    def setUpClass(cls):
        cls.prefs = {
            'profile.default_content_setting_values.automatic_downloads': 1}
        cls.options = webdriver.ChromeOptions()
        # cls.options.add_argument('--headless')
        cls.options.add_argument('--disable-dev-shm-usage')
        cls.options.add_argument('--ignore-certificate-errors')
        cls.options.add_argument('--ignore-ssl-errors')
        cls.options.add_experimental_option(
            'excludeSwitches', ['enable-logging'])
        cls.options.add_experimental_option('prefs', cls.prefs)
        cls.driver = webdriver.Chrome(
            ChromeDriverManager().install(), options=cls.options)
        cls.actions = ActionChains(cls.driver)
        cls.wait = WebDriverWait(cls.driver, 20)

    def test_detainee(self):
        """Get detainee"""
        driver = self.driver
        wait = self.wait

        login = LoginPage(driver, wait)
        report = ReportPage(driver, wait)
        niu = NIU(driver, wait)

        # Login
        driver.get("https://service.emedpractice.com/index.aspx")
        login.enter_username(config.loginid)
        login.enter_password(config.loginpassword)
        login.click_login()

        # Go to report page
        report.nav_reports()
        logger.info("Starting Date %s", day)

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
        page1 = niu.gen_final(visit, apt, cpt, page=1)
        page2 = niu.gen_final(cpt, visit, apt, page=2)

        # Write data into XLSX workbook
        xlsx = XLSX(day)
        xlsx.write_report(page1, page2)

        # Upload to Google Drive
        upload_xlsx(xlsx.file_name, xlsx.file_path)

        time.sleep(2)
        logger.info("Completed Execution")

    @classmethod
    def tearDownClass(cls):
        cls.driver.close()
        cls.driver.quit()
        print("Driver Closed")


if __name__ == '__main__':
    unittest.main()
