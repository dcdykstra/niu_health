from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from classes import *
from bs4 import BeautifulSoup
from functools import reduce

import datetime as dt
import pandas as pd

class NIU():
    def __init__(self, driver, wait) -> None:
        self.driver = driver
        self.wait = wait
        self.apt_table = '_ctl0_ContentPlaceHolder1_gvAppointments'
        self.pt_table = '_ctl0_ContentPlaceHolder1_gvCount'
        self.cpt_table = '_ctl0_ContentPlaceHolder1_gvreport'

        self.apt_df_columns = ['ID', 'Service Date', 'Reason', 'Time']
        self.pt_df_columns = ['ID', 'First Name', 'Last Name', 'DOB', 'Gender', 'Address', 'State', 'Zip', 'Visit Count']
        self.cpt_df_columns = ['ID', 'Assessment Date', 'CSAMI Code', 'CSAMI']

        self.apt_report = 'Appointments Report'
        self.pt_report = 'Patient Visit Report'
        self.cpt_report = 'CPT Code Report'

        self.report_tables = [self.apt_table, self.pt_table, self.cpt_table]
        self.report_columns = [self.apt_df_columns, self.pt_df_columns, self.cpt_df_columns]
        self.report_names = [self.apt_report, self.pt_report, self.cpt_report]

        self.report_zip = list(zip(self.report_tables, self.report_names, self.report_columns))
        #self.apt_download = 'Appointment'
        #self.pt_download = 'Patient'
        #self.cpt_download = 'CPT'

        #self.apt_href = 'AppointmentReportv1' 
        #self.pt_href = 'visitreport'
        #self.cpt_href = 'cpt_bills_reportV2'

        self.stage = ReportPage(self.driver, self.wait)

    def stage_apt(self, date_from_val, date_to_val):
        date_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, '_ctl0_ContentPlaceHolder1_ddltypes'))))
        date_select.select_by_value("R")
        self.stage.set_date("YTD", date_from_val, date_to_val)

    def stage_pt(self, date_from_val, date_to_val):
        facility_select = Select(self.wait.until(EC.presence_of_element_located((By.ID, '_ctl0_ContentPlaceHolder1_ddlfacility'))))
        facility_select.select_by_visible_text('HPD CRD')
        self_pay = self.wait.until(EC.element_to_be_clickable((By.ID, '_ctl0_ContentPlaceHolder1_ChkSelfPay')))
        self_pay.click()
        non_bill = self.wait.until(EC.element_to_be_clickable((By.ID, '_ctl0_ContentPlaceHolder1_ChkNonBillableEncounters')))
        non_bill.click()
        self.stage.set_date("YTD", date_from_val, date_to_val)

    def stage_cpt(self, date_from_val, date_to_val):
        date_select = Select(self.wait.until(EC.element_to_be_clickable((By.ID, '_ctl0_ContentPlaceHolder1_ddltypes'))))
        date_select.select_by_value("R")
        facility_label = self.wait.until(EC.visibility_of_element_located((By.XPATH, '//*[contains(text(), "HPD CRD PROGRAM")]'))).get_attribute("for")
        facility_check = self.wait.until(EC.visibility_of_element_located((By.ID, facility_label)))
        facility_check.click()
        self.stage.set_date("YTD", date_from_val, date_to_val)

    def gen_columns(self, df):
        ## AGE
        dob = "DOB"
        today = dt.datetime.today()
        df[dob] = pd.to_datetime(df[dob]) 
        df['Age'] = df[dob].apply(
                lambda x: today.year - x.year - 
                ((today.month, today.day) < (x.month, x.day)) 
                )
        df.loc[df['Age'] > 89, 'Age'] = '>90'
        df.loc[df['Age'] < 1, 'Age'] = 'INPUT ERROR'
        df[dob] = df[dob].dt.strftime('%m-%d-%Y') 

        ## CSAMI Count
        df["CSAMI Assessment Count"] = [len(str(x).split(",")) if len(str(x))>=5 else 0 for x in df["CSAMI Code"]]

    def scrape_table(self, table_id): 
        # table = self.wait.until(EC.presence_of_element_located((By.ID, f'{table_id}')))
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        table = soup.find('table', id=f'{table_id}')
        headers = []
        empty_dict = {}
        try:
            for header in table.find_all('th'):
                column = header.text
                headers.append(column)

            df = pd.DataFrame(columns = headers)

            for item in table.find_all('tr')[1:]:
                row_data = item.find_all('td')
                row = [header.text for header in row_data]
                length = len(df)
                df.loc[length] = row
            

            if table_id == self.apt_table: 
                # df.columns = df.columns.rstrip()
                df['ID'] = pd.to_numeric(df.iloc[:,7], errors='coerce')
                df['Time'] = df.iloc[:,1]
                df['Reason'] = df.iloc[:,11].str.upper()
                df['Service Date'] = pd.to_datetime(df.iloc[:,0], errors='coerce')
                # df[pd.notnull(df['Service Date'])]
                df['Service Date'] = df['Service Date'].dt.strftime('%m-%d-%Y') 
                df = df[self.apt_df_columns]
                assert (len(df)>1) and (df["ID"].isna()[0] == False)

            elif table_id == self.cpt_table: 
                # df.columns = df.columns.rstrip()
                # df = df.replace(r'^s*$', float('NaN'), regex = True)
                df['ID'] = pd.to_numeric(df.iloc[:,0], errors='coerce')
                df['Assessment Date'] = df.iloc[:,9]
                df['CSAMI Code'] = df.iloc[:,10]
                df['CSAMI'] = df.iloc[:,11]
                df = df[self.cpt_df_columns].replace('\n',' ')
                df = df.groupby(['ID', 'Assessment Date']).agg(', '.join).reset_index()
                assert (len(df)>1) and (df["ID"].isna()[0] == False)
                
            elif table_id == self.pt_table: 
                df['ID'] = pd.to_numeric(df.iloc[:,0], errors='coerce')
                df['Last Name'] = df.iloc[:,2].str.upper()
                df['First Name'] = df.iloc[:,3].str.upper()
                df['Gender'] = df.iloc[:,4]
                df['DOB'] = df.iloc[:,5]
                df['Address'] = df.iloc[:,6]
                df['State'] = df.iloc[:,9]
                df['Zip'] = df.iloc[:,10]
                df['Visit Count'] = df.iloc[:,17].str.strip()
                df = df[self.pt_df_columns]
                assert (len(df)>1) and (df["ID"].isna()[0] == False)

            else: 
                print('nothing')   

            df = df.dropna(subset = ['ID'])
            return df
        except:
            if table_id == self.apt_table:
                empty_dict['ID'] = 0
                empty_dict['Time'] = None
                empty_dict['Reason'] = None
                empty_dict['Service Date'] = None
            elif table_id == self.cpt_table:
                empty_dict['ID'] = 0
                empty_dict['Assessment Date'] = None
                empty_dict['CSAMI Code'] = None
                empty_dict['CSAMI'] = None
            else:
                empty_dict['ID'] = 0
                empty_dict['Last Name'] = None
                empty_dict['First Name'] = None
                empty_dict['Gender'] = None
                empty_dict['DOB'] = None
                empty_dict['Address'] = None
                empty_dict['State'] = None
                empty_dict['Zip'] = None
                empty_dict['Visit Count'] = None
        return pd.DataFrame(empty_dict, index=[0])

    def gen_final(self, *args, page):
        df_list = []
        for arg in args:
            df_list.append(arg)
        final = reduce(lambda x, y: pd.merge(x, y, on = 'ID', how='left'), df_list)

        self.gen_columns(final)
        
        if page == 1:
            ungrouped_vals = ['ID', 'Last Name', 'First Name', 'Age', 'DOB', 'Gender', 'Service Date', 'Time', 'Reason', 'CSAMI Assessment Count']
            final = final[ungrouped_vals]
            return final
        elif page == 2:
            grouped_vals = ['ID', 'Last Name', 'First Name', 'Age', 'DOB', 'Gender', 'Assessment Date', 'CSAMI Code', 'CSAMI']
            final = final[grouped_vals]
            return final

       