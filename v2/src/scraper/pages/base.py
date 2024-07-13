import os
import glob
import pandas as pd
from bs4 import BeautifulSoup

from src.config.configlog import config


class BasePage:
    """Main class item for the eMed site"""

    def __init__(self, driver) -> None:
        self.driver = driver.driver
        self.wait = driver.wait
        self.actions = driver.actions
        self.mydir = config.outputdir
        self.content = "_ctl0_ContentPlaceHolder1_gv"

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
