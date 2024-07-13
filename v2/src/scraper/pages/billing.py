from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from src.scraper.pages.base import BasePage

from src.config.configlog import config, logger


class BillingReport(BasePage):
    def select_dates(self, start, end):
        """Selects the dates for the report"""
        date_from = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[contains(@id, "txtFromDate")]'))
        )
        date_from.click()
        date_from.clear()
        date_from.send_keys(Keys.HOME)
        date_from.send_keys(start)

        date_to = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[contains(@id, "txtToDate")]'))
        )
        date_to.click()
        date_to.clear()
        date_to.send_keys(Keys.HOME)
        date_to.send_keys(end)

    def run_report(self):
        """Runs the report"""
        run_report = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[contains(@id, "RunItNow")]'))
        )
        run_report.click()
