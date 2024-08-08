from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from src.scraper.pages.base import BasePage

from src.config.configlog import config, logger

## NOT CURRENTLY USED


class PatientDetailsPage(BasePage):
    def nav_chart(self):
        go_to_chart = self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[contains(@id, "btnEMRSummary")]')
            )
        )
        go_to_chart.click()
