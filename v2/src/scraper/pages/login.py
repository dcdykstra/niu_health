from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from src.config.configlog import logger
from src.scraper.pages.base import BasePage


class LoginPage(BasePage):
    """Login Page for eMed"""

    def enter_username(self, username):
        """Enters user name to webpage"""
        self.driver.find_element(By.ID, "email").clear()
        self.driver.find_element(By.ID, "email").send_keys(username)
        logger.info("Entered Username")

    def enter_password(self, password):
        """Enters password to webpage"""
        self.driver.find_element(By.ID, "password").clear()
        self.driver.find_element(By.ID, "password").send_keys(password)
        logger.info("Entered Password")

    def click_login(self):
        """Click the login button"""
        login = self.driver.find_element(By.ID, "SigninBtn")
        login.click()

        try:
            cont = self.wait.until(
                EC.element_to_be_clickable((By.ID, "btnContinueLogin"))
            )
            cont.click()
        except Exception as error:
            print("No multiple logins - continue", error)
        logger.info("Clicked Login")
