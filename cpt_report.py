from selenium.webdriver.common.by import By

from classes import ReportPage

class CPTs_Report_Page(ReportPage):
    def __init__(self, driver, wait) -> None:
        super().__init__(self, driver, wait)
        self.href = "cpt_bills_reportV2"
        self.table_id = "report"
        self.cpt_txtbox_id = '_ctl0_ContentPlaceHolder1_txtcpt'

    # Enters CPT codes into box
    def enter_cpt_code(self, cpt_code):
        self.driver.find_element(By.ID, self.cpt_txtbox_id).clear()
        self.driver.find_element(By.ID, self.cpt_txtbox_id).send_keys(cpt_code)
