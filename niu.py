"""
There may be redundancies in this .py file vs the classes.py file but,
everything here is unique for the Detainee Data .XLSX workbook.
"""
import datetime as dt
from functools import reduce
import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from configlog import logger
from classes import ReportPage

class NIU():
    """The main code from eMed"""
    def __init__(self, driver, wait) -> None:
        self.driver = driver
        self.wait = wait

        # HTML table id's
        self.apt_table = '_ctl0_ContentPlaceHolder1_gvAppointments'
        self.pt_table = '_ctl0_ContentPlaceHolder1_gvCount'
        self.cpt_table = '_ctl0_ContentPlaceHolder1_gvreport'

        # Columns being saved from each table
        self.apt_df_columns = ['ID', 'Service Date', 'Reason', 'Time']
        self.pt_df_columns = ['ID', 'First Name', 'Last Name', 'DOB', 'Gender',
            'Address', 'State', 'Zip', 'Visit Count']
        self.cpt_df_columns = ['ID', 'Assessment Date', 'CSAMI Code', 'CSAMI']

        # Name of each report
        self.apt_report = 'Appointments Report'
        self.pt_report = 'Patient Visit Report'
        self.cpt_report = 'CPT Code Report'

        self.report_tables = [self.apt_table, self.pt_table, self.cpt_table]
        self.report_columns = [self.apt_df_columns, self.pt_df_columns, self.cpt_df_columns]
        self.report_names = [self.apt_report, self.pt_report, self.cpt_report]
        self.report_zip = list(zip(self.report_tables, self.report_names, self.report_columns))

        # Creating self.stage object for usage of functions from classes.py -> ReportPage()
        self.stage = ReportPage(self.driver, self.wait)
        self.validation = {}

    def stage_apt(self, date_from_val, date_to_val):
        """Staging appointment reports table
            Date range only
        """
        date_select = Select(self.wait.until(
            EC.element_to_be_clickable((By.ID, '_ctl0_ContentPlaceHolder1_ddltypes'))))
        date_select.select_by_value("R")
        self.stage.set_date("YTD", date_from_val, date_to_val)

    def stage_pt(self, date_from_val, date_to_val):
        """Staging patient visit report table
            Selecting HPD CRD, deselecting selfpay and nonbillable encounters
            Date range
        """
        facility_select = Select(self.wait.until(
            EC.presence_of_element_located((By.ID, '_ctl0_ContentPlaceHolder1_ddlfacility'))))
        facility_select.select_by_visible_text('HPD CRD')
        self_pay = self.wait.until(
            EC.element_to_be_clickable((By.ID, '_ctl0_ContentPlaceHolder1_ChkSelfPay')))
        self_pay.click()
        non_bill = self.wait.until(
            EC.element_to_be_clickable(
                (By.ID, '_ctl0_ContentPlaceHolder1_ChkNonBillableEncounters')))
        non_bill.click()
        self.stage.set_date("YTD", date_from_val, date_to_val)

    def stage_cpt(self, date_from_val, date_to_val):
        """Staging CPT report
          HPD CRD PROGRAM CPT Codes
          Date Range
        """
        date_select = Select(self.wait.until(
            EC.element_to_be_clickable((By.ID, '_ctl0_ContentPlaceHolder1_ddltypes'))))
        date_select.select_by_value("R")
        facility_label = self.wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, '//*[contains(text(), "HPD CRD PROGRAM")]'))).get_attribute("for")
        facility_check = self.wait.until(EC.visibility_of_element_located((By.ID, facility_label)))
        facility_check.click()
        self.stage.set_date("YTD", date_from_val, date_to_val)

    def gen_columns(self, data_frame):
        """Generates columns to be used in the XLSX workbook
            Age and CSAMI Assessment Count
        """
        dob = "DOB"
        today = dt.datetime.today()
        data_frame[dob] = pd.to_datetime(data_frame[dob])
        data_frame['Age'] = data_frame[dob].apply(
                lambda x: today.year - x.year -
                ((today.month, today.day) < (x.month, x.day))
                )
        data_frame.loc[data_frame['Age'] > 89, 'Age'] = '>90'
        data_frame.loc[data_frame['Age'] < 1, 'Age'] = 'INPUT ERROR'
        data_frame[dob] = data_frame[dob].dt.strftime('%m-%d-%Y')

        ## CSAMI Count
        data_frame["CSAMI Assessment Count"] = [len(str(x).split(","))
            if len(str(x))>=5 else 0 for x in data_frame["CSAMI Code"]]

    def scrape_table(self, table_id):
        """Multi-use function specifically for scraping tables
            from the 3 main reports for this workbook
            If no tables are present, it creates a dataframe with 1 row with all None values
        """
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        table = soup.find('table', id=f'{table_id}')
        headers = []
        empty_dict = {}
        try:
            for header in table.find_all('th'):
                column = header.text
                headers.append(column)

            data_frame = pd.DataFrame(columns = headers)

            for item in table.find_all('tr')[1:]:
                row_data = item.find_all('td')
                row = [header.text for header in row_data]
                length = len(data_frame)
                data_frame.loc[length] = row

            if table_id == self.apt_table:
                logger.info("Appointment Table has data")
                data_frame['ID'] = pd.to_numeric(data_frame.iloc[:,7], errors='coerce')
                data_frame['Time'] = data_frame.iloc[:,1]
                data_frame['Reason'] = data_frame.iloc[:,11].str.upper()
                data_frame['Service Date'] = pd.to_datetime(data_frame.iloc[:,0], errors='coerce')
                data_frame['Service Date'] = data_frame['Service Date'].dt.strftime('%m-%d-%Y')
                data_frame = data_frame[self.apt_df_columns]
                assert (len(data_frame)>1) and (not data_frame["ID"].isna()[0])

            elif table_id == self.cpt_table:
                logger.info("CPT Code Table has data")
                data_frame['ID'] = pd.to_numeric(data_frame.iloc[:,0], errors='coerce')
                data_frame['Assessment Date'] = data_frame.iloc[:,9]
                data_frame['CSAMI Code'] = data_frame.iloc[:,10]
                data_frame['CSAMI'] = data_frame.iloc[:,11]
                data_frame = data_frame[self.cpt_df_columns].replace('\n',' ')
                data_frame = data_frame.groupby(
                    ['ID', 'Assessment Date']).agg(', '.join).reset_index()
                assert (len(data_frame)>1) and (not data_frame["ID"].isna()[0])

            elif table_id == self.pt_table:
                logger.info("Patient Visit Table has data")
                data_frame['ID'] = pd.to_numeric(data_frame.iloc[:,0], errors='coerce')
                data_frame['Last Name'] = data_frame.iloc[:,2].str.upper()
                data_frame['First Name'] = data_frame.iloc[:,3].str.upper()
                data_frame['Gender'] = data_frame.iloc[:,4]
                data_frame['DOB'] = data_frame.iloc[:,5]
                data_frame['Address'] = data_frame.iloc[:,6]
                data_frame['State'] = data_frame.iloc[:,9]
                data_frame['Zip'] = data_frame.iloc[:,10]
                data_frame['Visit Count'] = data_frame.iloc[:,17].str.strip()
                data_frame = data_frame[self.pt_df_columns]
                assert (len(data_frame)>1) and (not data_frame["ID"].isna()[0])

            else:
                print('nothing')

            data_frame = data_frame.dropna(subset = ['ID'])
            return data_frame
        except Exception as error_caught:
            if table_id == self.apt_table:
                logger.warning("Appointment Table empty")
                empty_dict['ID'] = 0
                empty_dict['Time'] = None
                empty_dict['Reason'] = None
                empty_dict['Service Date'] = None
            elif table_id == self.cpt_table:
                logger.warning("CPT Code Table empty")
                empty_dict['ID'] = 0
                empty_dict['Assessment Date'] = None
                empty_dict['CSAMI Code'] = None
                empty_dict['CSAMI'] = None
            else:
                logger.warning("Patient Visit Table empty")
                empty_dict['ID'] = 0
                empty_dict['Last Name'] = None
                empty_dict['First Name'] = None
                empty_dict['Gender'] = None
                empty_dict['DOB'] = None
                empty_dict['Address'] = None
                empty_dict['State'] = None
                empty_dict['Zip'] = None
                empty_dict['Visit Count'] = None
            logger.warning("Something went wrong in patient table %s", error_caught)
        return pd.DataFrame(empty_dict, index=[0])

    def gen_final(self, *args, page):
        """Generates the final dataframe to be used in the XLSX writer.
            Reorders columns
        """
        df_list = []
        for arg in args:
            df_list.append(arg)
        final = reduce(lambda x, y: pd.merge(x, y, on = 'ID', how='left'), df_list)

        self.gen_columns(final)

        if page == 1:
            ungrouped_vals = ['ID', 'Last Name', 'First Name', 'Age',
                'DOB', 'Gender', 'Service Date', 'Time', 'Reason', 'CSAMI Assessment Count']
            final = final[ungrouped_vals]
            return final
        if page == 2:
            grouped_vals = ['ID', 'Last Name', 'First Name', 'Age',
                'DOB', 'Gender', 'Assessment Date', 'CSAMI Code', 'CSAMI']
            final = final[grouped_vals]
            return final
