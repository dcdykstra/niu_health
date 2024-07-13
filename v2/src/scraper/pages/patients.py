from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from src.scraper.pages.base import BasePage

from src.config.configlog import config, logger

## NOT CURRENTLY USED


class PatientsPage(BasePage):
    def select_dates(self, start, end):
        """Selects the dates for the report"""
        logger.info(f"Selected Dates {start} to {end}")
        date_from = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[contains(@id, "txtDateFrom")]'))
        )
        date_from.click()
        date_from.clear()
        date_from.send_keys(Keys.HOME)
        logger.info(f"Send keys date_from {start}")
        date_from.send_keys(start)

        date_to = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[contains(@id, "txtDateTo")]'))
        )
        date_to.click()
        date_to.clear()
        date_to.send_keys(Keys.HOME)
        logger.info(f"Send keys date_to {end}")
        date_to.send_keys(end)

    def pull(self):
        self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[contains(@id, "CurrentPatient")]')
            )
        )
        soup = self.make_soup()
        table = soup.find("table", {"id": "_ctl0_ContentPlaceHolder1_gvCurrentPatient"})
        body = table.find("tbody")
        columns = table.find("thead").find_all("th")
        rows = body.find_all("tr")

        logger.info(f"Found table with {len(columns)} columns")
        logger.info(f"Found table with {len(rows)} rows")

        # Extract the column names
        column_names = [column.text for column in columns]
        logger.info(f"Columns: {column_names}")

        # Get the value of each row
        for row in rows:
            data = row.find_all("td")
            values = [datum.text for datum in data]
            logger.info(f"Row: {values}")

    def enter_chart_number(self, chart_number):
        """Inputs the chart number"""
        chart = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[contains(@id, "txtPatientID")]'))
        )
        chart.click()
        chart.clear()
        chart.send_keys(chart_number)
        logger.info(f"Input chart number: {chart_number}")

    def click_search(self):
        """Clicks the search button"""
        search = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[contains(@id, "btnSearch")]'))
        )
        search.click()
        logger.info("Clicked Search")

    def click_patient(self):
        """Clicks the patient"""
        patient = self.wait.until(
            EC.element_to_be_clickable(
                (By.ID, "_ctl0_ContentPlaceHolder1_gvCurrentPatient__ctl2_hlSelect")
            )
        )
        patient.click()
        logger.info("Clicked Patient")
