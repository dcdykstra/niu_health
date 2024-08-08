from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from src.config.configlog import logger
from src.scraper.pages.base import BasePage


class ContentPage(BasePage):
    """The main content page of eMed"""

    def nav_reports(self):
        """Navigates to the reports page"""
        self.reset_iframe()
        self.reports_menu = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//a[contains(@href, "tabname=Reports")]')
            )
        )
        self.reports_menu.click()
        logger.info("Navigated to Reports Page")

    def nav_vistreport(self):
        self.reset_iframe()
        pt_reports = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//a[contains(@label, "Patient Reports")]')
            )
        )
        pt_reports.click()
        menu_item = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//a[contains(@href, "visitreport")]')
            )
        )
        menu_item.click()
        content_iframe = self.wait.until(
            EC.presence_of_element_located((By.ID, "contentframe"))
        )
        self.driver.switch_to.frame(content_iframe)
        logger.info("Navigated to Visit Report Page")

    def nav_patients(self):
        """Navigates to the patient's page"""
        self.reset_iframe()
        nav_menu = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//a[contains(@href, "tabname=Patients")]')
            )
        )
        nav_menu.click()
        content_iframe = self.wait.until(
            EC.presence_of_element_located((By.ID, "contentframe"))
        )
        self.driver.switch_to.frame(content_iframe)
        logger.info("Navigated to Patients Page")

    def nav_practice(self):
        """Navigates to the practice page"""
        self.reset_iframe()
        nav_menu = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//a[contains(@href, "tabname=Facilities")]')
            )
        )

        self.actions.move_to_element(nav_menu).perform()

        nav_item = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="Banner_navMenu"]/ul/li[5]/ul/li[8]/a')
            )
        )

        nav_item.click()

        content_iframe = self.wait.until(
            EC.presence_of_element_located((By.ID, "contentframe"))
        )
        self.driver.switch_to.frame(content_iframe)
        logger.info("Navigated to Practice Page")
