from io import StringIO
import pandas as pd

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from src.scraper.pages.base import BasePage
from src.config.configlog import logger, config


class PracticePage(BasePage):
    def nav_favorites(self):
        """Navigates to the favorites page"""
        self.reset_iframe()
        content_iframe = self.wait.until(
            EC.presence_of_element_located((By.ID, "contentframe"))
        )
        self.driver.switch_to.frame(content_iframe)
        nav_menu = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//a[contains(@href, "cpt_favorites")]')
            )
        )
        nav_menu.click()
        logger.info("Navigated to Favorites Page")

    def select_crd(self):
        select = Select(
            self.wait.until(EC.presence_of_element_located((By.ID, "ddlchargestype")))
        )
        select.select_by_visible_text(config.cptgroup)

    def scrape_cpts(self):
        """Scrapes the CPT codes from the favorites page"""
        self.wait.until(EC.presence_of_element_located((By.ID, "gvfavorite_cpt")))
        soup = self.make_soup()
        table = soup.find("table", {"id": "gvfavorite_cpt"})
        cpts = []
        for row in table.find_all("tr")[1:]:
            cells = row.find_all("td")
            code = cells[0].text
            cpt_description = cells[1].text
            cpt = {"code": code, "description": cpt_description}
            cpts.append(cpt)

        df = pd.DataFrame([s for s in cpts])
        return df

    def get_wd_codes(self, df):
        df = df[df["description"].str.contains("WITHDRAWAL")]
        return df["code"].tolist()
