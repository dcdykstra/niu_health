import pandas as pd

from io import StringIO

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys

from src.scraper.pages.base import BasePage

from src.config.configlog import logger


class CPTsReport(BasePage):
    HREF = "cpt_bills_reportV2"
    TABLE_ID = "_ctl0_ContentPlaceHolder1_gvreport"
    CPT_TXTBOX_ID = "_ctl0_ContentPlaceHolder1_txtcpt"

    # Enters CPT codes into box
    def enter_cpt_code(self, cpt_code):
        self.driver.find_element(By.ID, self.CPT_TXTBOX_ID).clear()
        self.driver.find_element(By.ID, self.CPT_TXTBOX_ID).send_keys(cpt_code)

    def select_search_by(self, dropdown_value):
        """Select by value `dropdown_value`
        T = Today
        W = Week
        M = Month
        R = Date Range
        """
        search_by = self.wait.until(
            EC.element_to_be_clickable((By.ID, "_ctl0_ContentPlaceHolder1_ddltypes"))
        )
        selected_button = Select(search_by)
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
                    "//*[contains(@id, '_ctl0_ContentPlaceHolder1_btnRunItNow')]",
                )
            )
        )
        submit.click()

    def scrape_table(self):
        """Need to scrape table since download buttons don't function properly"""
        self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[contains(@id, "_ctl0_ContentPlaceHolder1_gvreport")]')
            )
        )

        soup = self.make_soup()
        table = soup.find("table", {"id": "_ctl0_ContentPlaceHolder1_gvreport"})
        body = table.find("tbody")
        columns = table.find("thead").find_all("th")
        rows = body.find_all("tr")

        logger.info(f"Found CPT Report table with {len(columns)} columns")
        logger.info(f"Found CPT Report table with {len(rows)} rows")

        column_names = [column.text for column in columns]
        logger.info(f"Columns: {column_names}")

        df = pd.read_html(StringIO(str(table)))[0]

        return df
