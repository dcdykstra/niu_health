import pandas as pd

from io import StringIO

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from src.scraper.pages.base import BasePage

from src.config.configlog import logger


class VisitsReport(BasePage):
    def stage_visits(self, start_date, end_date):
        """Stages the visit report"""
        self_pay = self.wait.until(
            EC.element_to_be_clickable((By.ID, "_ctl0_ContentPlaceHolder1_ChkSelfPay"))
        )
        self_pay.click()
        non_bill = self.wait.until(
            EC.element_to_be_clickable(
                (By.ID, "_ctl0_ContentPlaceHolder1_ChkNonBillableEncounters")
            )
        )
        non_bill.click()
        distinct_patients = self.wait.until(
            EC.element_to_be_clickable(
                (By.ID, "_ctl0_ContentPlaceHolder1_chkdistinct_patient")
            )
        )
        distinct_patients.click()

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
            EC.element_to_be_clickable((By.XPATH, "//*[contains(@id, 'btnsubmit')]"))
        )
        submit.click()

    def download_csv(self):
        """Downloads the CSV file"""
        download = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//*[contains(@id, 'imgCSV')]"))
        )
        download.click()
