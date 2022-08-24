from selenium.webdriver.common.by import By
from unidecode import unidecode

from classes import ReportPage

class APT_Report(ReportPage):
    def __init__(self, driver, wait) -> None:
        super().__init__(self, driver, wait)
        self.href = "AppointmentReportv1"
        self.table_id = "Appointments"
        self.select_all_id = "_ctl0_ContentPlaceHolder1_chkSelectAllProviders"

    # Deselects all the encounter providers
    def deselect_ep(self):
        chk = self.driver.find_element(By.ID, self.select_all_id)
        if chk.get_attribute("checked"):
            chk.click()
        else:
            print("Already Unchecked")

    # Selects a single encounter provider
    def select_ep(self, name):
        soup = self.make_soup()
        table = soup.find_all("table", id = "_ctl0_ContentPlaceHolder1_chkProvider")
        body = table[0].find("tbody")

        for i in body.find_all("label"):
            if unidecode(i.text) in name:
                id = i.get("for")
                btn = self.driver.find_element(By.ID, id)
                btn.click()
