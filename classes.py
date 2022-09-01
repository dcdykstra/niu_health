"""
Page Navigation Class helpers
"""
from datetime import timedelta
from datetime import datetime
import os
import glob
import re
import pandas as pd

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (TimeoutException,
                                        NoSuchElementException,
                                        NoSuchWindowException)
from unidecode import unidecode
from configlog import config, logger


class WebPage():
    """Main class item for the eMed site"""
    def __init__(self, driver, wait) -> None:
        self.driver = driver
        self.wait = wait
        self.mydir = config.outputdir
        self.content = '_ctl0_ContentPlaceHolder1_gv'

    def make_soup(self):
        """Generates the bs4 html for the page"""
        return BeautifulSoup(self.driver.page_source, "html.parser")

    def reset_iframe(self):
        """Resets the iframe to the default iframe"""
        self.driver.switch_to.default_content()

    def merge(self, savefile):
        """
            merge(savefile) is for merging files after being collected in the data folder.
            Mostly been used to combine .csv files after
            set_date_month(tableid, date_from_val, date_to_val) and
            set_date_submit(tableid, date_from_val, date_to_val, day_intervals)
        """
        files = os.path.join(self.mydir, "*.csv")
        files = glob.glob(files)
        data_file = pd.concat(map(pd.read_csv, files), ignore_index=True)
        data_file = data_file.iloc[:, 1:]
        data_file = data_file.drop_duplicates()
        data_file.to_csv(savefile)


class LoginPage(WebPage):
    """Login Page for eMed"""
    def enter_username(self, username):
        """Enters user name to webpage"""
        self.driver.find_element(By.ID, 'email').clear()
        self.driver.find_element(By.ID, 'email').send_keys(username)
        logger.info("Entered Username")

    def enter_password(self, password):
        """Enters password to webpage"""
        self.driver.find_element(By.ID, 'password').clear()
        self.driver.find_element(By.ID, 'password').send_keys(password)
        logger.info("Entered Password")

    def click_login(self):
        """Click the login button"""
        login = self.driver.find_element(By.ID, "SigninBtn")
        login.click()

        try:
            cont = self.wait.until(
                EC.element_to_be_clickable((By.ID, 'btnContinueLogin')))
            cont.click()
        except Exception as error:
            print("No multiple logins - continue", error)
        logger.info("Clicked Login")


class ContentPage(WebPage):
    """The main content page of eMed"""
    def nav_reports(self):
        """Navigates to the reports page"""
        self.reset_iframe()
        self.reports_menu = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, '//a[contains(@href, "tabname=Reports")]')))
        self.reports_menu.click()
        logger.info("Navigated to Reports Page")


    def nav_patients(self):
        """Navigates to the patient's page"""
        self.reset_iframe()
        nav_menu = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, '//a[contains(@href, "tabname=Patients")]')))
        nav_menu.click()
        content_iframe = self.wait.until(
            EC.presence_of_element_located((By.ID, 'contentframe')))
        self.driver.switch_to.frame(content_iframe)
        logger.info("Navigated to Patients Page")


class ReportPage(ContentPage):
    """The report page in eMed"""
    def load_report(self, report_href):
        """Loads a specific report page based on href key
          Must nav_reports() first
        """
        self.reset_iframe()
        content_iframe = self.wait.until(
            EC.presence_of_element_located((By.ID, 'contentframe')))
        self.driver.switch_to.frame(content_iframe)
        report = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, f'//a[contains(@href, "{report_href}")]')))
        self.driver.execute_script("arguments[0].click();", report)
        report_iframe = self.wait.until(
            EC.presence_of_element_located((By.ID, 'ReportMasterFrame')))
        self.driver.switch_to.frame(report_iframe)
        logger.info("Loaded Report %s", report_href)

    def pull(self, tableid, savefile):
        """Pulls data from the table.
         3 Different types of tableid's ("report", "Appointments", "Count")
        """
        try:
            # report, Appointments, Count
            table = self.wait.until(EC.presence_of_element_located(
                (By.ID, self.content+tableid)))
            soup = self.make_soup()
            table = soup.find_all("table", id=self.content+tableid)
            body = table[0].find("tbody")

            head = table[0].find("thead").find_all("th")
            cpt_headers = [unidecode(i.text.strip()) for i in head]

            temp = []
            for i in body.find_all("tr"):
                temp.append([unidecode(j.text) for j in i.find_all("td")])

            data_frame = pd.DataFrame(temp, columns=cpt_headers)
            data_frame["Bill#"] = data_frame["Bill#"].apply(lambda x: x.strip("\n"))
            data_frame.drop(data_frame.tail(1).index, inplace=True)
            data_frame.to_csv(savefile)
            logger.info("Pulled data from %s Table", tableid)

        except TimeoutException:
            logger.info("TimeoutException: Failed to pull data")
            print("No Table")

    def select_dates(self, start, end):
        """Function to select dates when a date range option exists"""
        date_from = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//*[contains(@id, "txtFrom")]')))
        date_from.clear()
        date_from.click()
        date_from.send_keys(start)
        date_to = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//*[contains(@id, "txtTo")]')))
        date_to.clear()
        date_to.click()
        date_to.send_keys(end)
        date_to.send_keys(Keys.ENTER)

    def set_date(self, date_option, date_from_val, date_to_val):
        """Sets date to correct values"""
        if date_option == 'Daily':
            self.select_dates(date_to_val, date_to_val)
        elif date_option == 'YTD':
            self.select_dates(date_from_val, date_to_val)

    def date_range_greater_than_28(self, startday, endday, day_intervals):
        """Splits a date range into processable day intervals to avoid downloads"""
        start = datetime.strptime(startday, "%m-%d-%Y")
        end = datetime.strptime(endday, "%m-%d-%Y")
        diff = (end - start)
        mod_diff = diff.days//day_intervals

        temp = []
        if diff.days > day_intervals:
            while mod_diff > 0:
                temp.append([start, start+timedelta(days=day_intervals)])
                start = (start+timedelta(days=day_intervals))
                mod_diff -= 1
            temp.append([start, end])
        else:
            temp.append([start, end])

        res = []
        for i in temp:
            res.append([j.strftime("%m-%d-%Y") for j in i])
        return res

    def set_date_submit(self, tableid, date_from_val, date_to_val, day_intervals=28):
        """Pulls data by a date range
        Used for specific date ranges or single days
        Avoid using for large date ranges
        day_intervals = 28 is to avoid an eMed issue where they
            don't allow you to pull data for greater
            than 1 month (28 days because of February)
        """
        split_range = self.date_range_greater_than_28(
            date_from_val, date_to_val, day_intervals)
        date_select = Select(self.wait.until(EC.element_to_be_clickable(
            (By.ID, '_ctl0_ContentPlaceHolder1_ddltypes'))))
        date_select.select_by_value("R")

        for i, j in enumerate(split_range):
            self.set_date("YTD", j[0], j[1])
            self.pull(tableid, savefile=os.path.join(
                self.mydir, f"temp{i}.csv"))

    def set_date_month(self, tableid, date_from_val, date_to_val):
        """Pulls data by month
        Use this when pulling data from Year to Date or Month to Date
        month, year
        """
        dates = pd.period_range(date_from_val, date_to_val, freq="M").strftime("%B %Y")
        selected_button = Select(self.wait.until(
            EC.element_to_be_clickable((By.ID, '_ctl0_ContentPlaceHolder1_ddltypes'))))
        selected_button.select_by_value("M")

        for i, j in enumerate(list(dates)):
            month = j.split()[0]
            year = j.split()[1]
            mo_select = Select(self.wait.until(EC.element_to_be_clickable(
                (By.ID, '_ctl0_ContentPlaceHolder1_ddlmonth'))))
            mo_select.select_by_visible_text(str(month))
            yr_select = Select(self.wait.until(EC.element_to_be_clickable(
                (By.ID, '_ctl0_ContentPlaceHolder1_ddlyear'))))
            yr_select.select_by_visible_text(str(year))

            run = self.driver.find_element(
                By.XPATH, '//*[@id="_ctl0_ContentPlaceHolder1_btnRunItNow"]')
            run.click()
            self.pull(tableid, savefile=os.path.join(
                self.mydir, f"{str(i)+month+year}.csv"))

class PatientPage(ContentPage):
    """Specifically created to pull patient demographic data"""
    def patients_search_dict(self):
        """Creates a dictionary of keys to search by in the patient search page"""
        self.nav_patients()
        soup = self.make_soup()
        inputs = soup.find_all("input", class_=re.compile(
            "text ui-widget-content ui-corner-all"))
        keys = []
        vals = []
        for i in inputs:
            vals.append(i.get("id"))
        spans = soup.find_all(
            "span", id=re.compile("_ctl0_ContentPlaceHolder1_lbl"),
            style="color:Black;font-family:verdana;font-size:8pt;"\
            "font-weight:normal;text-decoration:none;")
        for i in spans:
            keys.append(i.text)
        return dict(zip(keys, vals))

    def search_patients(self, key, value):
        """Searches for a patient when on the patient search page with a key and value"""
        query_select = self.wait.until(EC.element_to_be_clickable(
            (By.ID, self.patients_search_dict().get(key))))
        query_select.clear()
        query_select.click()
        query_select.send_keys(value, Keys.RETURN)

    def open_patient_file(self, chart):
        """Opens a patient file based on a chart number"""
        self.reset_iframe()
        self.nav_patients()
        self.search_patients("Chart#", chart)
        button = self.driver.find_element(
            By.ID, '_ctl0_ContentPlaceHolder1_gvCurrentPatient__ctl2_hlSelect')
        button.click()

        demo = self.driver.find_element(
            By.XPATH, '//a[contains(@href, "PatientDetails")]')
        demo.click()

    def pull_patient_data(self):
        """Pulls patient data from their demo page"""
        soup = self.make_soup()
        txt_inp = soup.find_all("input", type="text",
                                id=re.compile("_ctl0_ContentPlaceHolder1"))
        opt_sel = soup.find_all(
            "select", id=re.compile("_ctl0_ContentPlaceHolder1"))
        btn_inp = soup.find_all("input", type="radio")
        chk_inp = soup.find_all("input", type="checkbox")
        order = ["Ethnicity *", "Sex *", "Date Of Birth *", "Country*", "State *",
            'Preferred Language', "Preferred Contact", 'Ok to receive msgs',
            'App.Reminder Contact', "Status", 'Marital Status *',
            "How did you find us?", "Gender Identity", "Sexual Orientation",
            "Facility", 'Automatically update Demographics information for self insured',
            'Automatically update Address information in insurance (other relations)']

        txt_dict = {}
        for i in txt_inp:
            txt_key = unidecode(i.parent.find_previous("span").text)
            if txt_key == "Date Of Birth *":
                date_time = datetime.strptime(i.get("value"), "%m/%d/%Y")
                txt_dict[txt_key] = date_time.year
            elif txt_key in order:
                txt_dict[txt_key] = i.get("value")

        opt_dict = {}
        for i in opt_sel:
            opt_key = unidecode(i.parent.find_previous("span").text)
            if opt_key in order:
                selected = i.findChild("option", selected="selected")
                if (selected is None) or (selected.text in [None, "--Select--", "-Select-"]):
                    opt_dict[opt_key] = None
                else:
                    opt_dict[opt_key] = selected.text

        btn_dict = {}
        for i in btn_inp:
            btn_key = unidecode(i.find_previous("span").text)
            if i.get("checked") == "checked":
                if i.get("name") == "_ctl0:ContentPlaceHolder1:Sex":
                    btn_dict["Sex *"] = btn_key

        race_dict = {}
        chk_dict = {}
        for i in chk_inp:
            if i.get("checked") == "checked":
                if i.get('title') is not None:
                    race_dict[i.get("title")] = 1
                else:
                    chk_dict[unidecode(i.nextSibling.text)] = 1
            else:
                if i.get('title') is not None:
                    race_dict[i.get("title")] = 0
                else:
                    chk_dict[unidecode(i.nextSibling.text)] = 0

        order = order + list(race_dict.keys())

        final_dict = {**txt_dict, **race_dict,
                      **chk_dict, **btn_dict, **opt_dict}

        return {k: final_dict[k] for k in order}

    # WIP
    def pull_data_ls(self, chart_ls):
        """Pull patient demographic data based on a list of chart numbers
            and return a dataframe of all the patient data"""
        failed = []
        data_frame = []
        for i in chart_ls:
            try:
                self.open_patient_file(str(i))
                temp = self.pull_patient_data()
                temp.update({"Chart #": i})
                data_frame.append(temp)
            except (NoSuchElementException) as error:
                print(error)
                failed.append(i)
                pd.DataFrame(failed).to_csv(
                    os.path.join(self.mydir, "failed.csv"))
                pd.DataFrame(data_frame).to_csv(os.path.join(self.mydir, "pulled.csv"))
                continue
            except (NoSuchWindowException) as error:
                print(error)
                failed.append(i)
                pd.DataFrame(failed).to_csv(
                    os.path.join(self.mydir, "failed.csv"))
                pd.DataFrame(data_frame).to_csv(os.path.join(self.mydir, "pulled.csv"))
                break
        pd.DataFrame(data_frame).to_csv(os.path.join(self.mydir, "pulled.csv"))

        # try:
        #     df = []
        #     for i in chart_ls:
        #         self.open_patient_file(str(i))
        #         temp = self.pull_patient_data()
        #         temp.update({"Chart #" : i})
        #         df.append(temp)
        #     pd.DataFrame(df).to_csv(os.path.join(self.mydir, "pulled.csv"))

        # except:
        #     failed.append(i)
        #     pd.DataFrame(failed).to_csv(os.path.join(self.mydir, "failed.csv"))
        #     continue
        # pd.DataFrame(df).to_csv(os.path.join(self.mydir, "pulled.csv"))

    def prep_pull(self, file):
        """Prepares a dataframe for pull_data_ls()
            Removes Chart # = 0, gets unique Chart #'s
        """
        data_frame = pd.read_csv(os.path.join(self.mydir, file), index_col=0)
        data_frame.drop(data_frame[data_frame["Chart #"] == 0].index)
        chart = pd.unique(data_frame["Chart #"]).tolist()

        pd.DataFrame(chart).to_csv(os.path.join(self.mydir, "chart.csv"))

        return chart
