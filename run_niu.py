from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains 
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import unittest
import time

from classes import *
from niu import NIU
from xlsx_writer_niu import XLSX

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
        driver = self.driver
        wait = self.wait

        login = LoginPage(driver, wait)
        report = ReportPage(driver, wait)
        niu = NIU(driver, wait)
        dates = ["08-07-2022"]

        driver.get("https://service.emedpractice.com/index.aspx")
        login.enter_username("")
        login.enter_password("")
        login.click_login()

        report.nav_reports()
        for date in dates:
            report.load_report("AppointmentReportv1")
            niu.stage_apt(date, date)
            apt = niu.scrape_table("_ctl0_ContentPlaceHolder1_gvAppointments")

            report.load_report("visitreport")
            niu.stage_pt(date, date)
            visit = niu.scrape_table("_ctl0_ContentPlaceHolder1_gvCount")

            report.load_report("cpt_bills_reportV2")
            niu.stage_cpt(date, date)
            cpt = niu.scrape_table("_ctl0_ContentPlaceHolder1_gvreport")

            p1 = niu.gen_final(visit, apt, cpt, page = 1)
            p2 = niu.gen_final(cpt, visit, apt, page = 2)
            
            xlsx = XLSX(date)
            xlsx.write_report(p1, p2)

        time.sleep(5)


    @classmethod
    def tearDownClass(cls):
        cls.driver.close()
        cls.driver.quit()
        print("Driver Closed")

if __name__ == '__main__':
    unittest.main()