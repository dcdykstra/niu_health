import pandas as pd

from io import StringIO

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys

from scraper.pages.base import BasePage

from config.configlog import logger


class AppointmentsReport(BasePage):
    HREF = "AppointmentReportv1"
    TABLE_ID = "_ctl0_ContentPlaceHolder1_gvAppointments"
    CPT_TXTBOX_ID = "_ctl0_ContentPlaceHolder1_txtcpt"

    def select_search_by(self, dropdown_value):
        """Select by value `dropdown_value`
        T = Today
        W = Week
        M = Month
        R = Date Range
        """
        selected_button = Select(
            self.wait.until(
                EC.element_to_be_clickable(
                    (By.ID, "_ctl0_ContentPlaceHolder1_ddltypes")
                )
            )
        )
        selected_button.select_by_value(dropdown_value)

    def select_date_range(self, start_date, end_date):
        date_from = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[contains(@id, "txtFrom")]'))
        )
        date_from.click()
        date_from.clear()
        date_from.send_keys(Keys.HOME)
        date_from.send_keys(start_date)

        date_to = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[contains(@id, "txtTo")]'))
        )
        date_to.click()
        date_to.clear()
        date_to.send_keys(Keys.HOME)
        date_to.send_keys(end_date)

    def click_submit(self):
        """Clicks the submit button"""
        submit = self.wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//*[contains(@id, '_ctl0_ContentPlaceHolder1_btnSearch')]",
                )
            )
        )
        submit.click()

    def download_csv(self):
        """Downloads the CSV file"""
        download = self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//*[contains(@id, '_ctl0_ContentPlaceHolder1_imgCSV')]")
            )
        )
        download.click()
