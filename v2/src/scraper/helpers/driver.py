from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


class Driver:
    """Driver class"""

    ## init driver
    def __init__(self, driver) -> None:
        self.driver = driver

    @classmethod
    def get_driver(cls, download_path):
        cls.prefs = {
            "profile.default_content_setting_values.automatic_downloads": 1,
            "download.default_directory": download_path,
        }
        cls.options = webdriver.ChromeOptions()
        cls.options.add_argument("--headless")
        cls.options.add_argument("--no-sandbox")
        cls.options.add_argument("--disable-dev-shm-usage")
        cls.options.add_argument("--ignore-certificate-errors")
        cls.options.add_argument("--ignore-ssl-errors")
        cls.options.add_experimental_option("excludeSwitches", ["enable-logging"])
        cls.options.add_experimental_option("prefs", cls.prefs)
        cls.options.add_argument("--disable-blink-features=AutomationControlled")
        cls.driver = webdriver.Chrome(
            options=cls.options, service=ChromeService(ChromeDriverManager().install())
        )
        # cls.driver = webdriver.Chrome(
        #     options=cls.options, service=ChromeService("/usr/local/bin/chromedriver")
        # )

        cls.wait = WebDriverWait(cls.driver, 20)
        cls.actions = webdriver.ActionChains(cls.driver)
        print("Driver Set Up")
        return cls

    @classmethod
    def tear_down_class(cls):
        cls.driver.close()
        cls.driver.quit()
        print("Driver Closed")
