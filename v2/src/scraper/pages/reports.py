from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from src.scraper.pages.base import BasePage
from src.config.configlog import logger


class ReportsPage(BasePage):
    def load_report(self, report_href):
        """Loads a specific report page based on href key
        Must nav_reports() first
        """
        self.reset_iframe()
        content_iframe = self.wait.until(
            EC.presence_of_element_located((By.ID, "contentframe"))
        )
        self.driver.switch_to.frame(content_iframe)
        report = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, f'//a[contains(@href, "{report_href}")]')
            )
        )
        self.driver.execute_script("arguments[0].click();", report)
        report_iframe = self.wait.until(
            EC.presence_of_element_located((By.ID, "ReportMasterFrame"))
        )
        self.driver.switch_to.frame(report_iframe)
        logger.info("Loaded Report %s", report_href)
