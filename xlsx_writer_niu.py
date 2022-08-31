from distutils.command.config import config
import imp
import pandas as pd
import os
from classes import *
from configlog import config

class XLSX():
    def __init__(self, date) -> None:
        self.subdir = config.outputdir
        self.workbook_dict = {}
        self.date = date
        self.file_name = f'Detainee_List_{self.date}.xlsx'
        self.sheet1= f'{self.date}_CRD List'
        self.sheet2= 'CSAMI Screening History'

    # No longer necessary
    def get_col_widths(self, dataframe):
        # First we find the maximum length of the index column
        idx_max = max([len(str(s)) for s in dataframe.index.values] +
                      [len(str(dataframe.index.name))])
        # Then, we concatenate this to the max of the lengths of column name and its values for each column, left to right
        return [idx_max] + [max([len(str(s)) for s in dataframe[col].values] + [len(col)]) for col in dataframe.columns]

    def sheet_entry(self, sel_date, name, title, subheader, df):
        keys = ['sel_date', 'name', 'title', 'subheader', 'df']
        values = sel_date, name, title, subheader, df
        sheet_dict = dict(zip(keys, values))
        self.workbook_dict[sel_date + '-' + name] = sheet_dict

    def write_report(self, df1, df2):
        writer = pd.ExcelWriter(os.path.join(self.subdir, self.file_name), engine='xlsxwriter')

        sheets_in_writer = [self.sheet1, self.sheet2]
        df_for_writer=[df1, df2]
        daily_sheet_titles = ['Summary Detainee List', 'Detainess with CSAMI Data']
        daily_sheet_subheaders = [f'Collection Date: {self.date}', '*Includes assemssent REFUSED']

        sh_tuples = [(df_for_writer), (sheets_in_writer), (daily_sheet_titles), (daily_sheet_subheaders)]
        for i, j, k, l in zip(*sh_tuples):
            i.to_excel(writer,j,startrow=2, index=False)

            ### Assign WorkBook
            workbook = writer.book
            # Add a header format
            header_format = workbook.add_format({'bold': True,'text_wrap': True,'size':11, 'align':'center', 'valign': 'top','fg_color': '#56b196','border': 1})
        for i, j, k, l in zip(*sh_tuples):
        #    for col, width in enumerate(get_col_widths(i)):
        #       writer.sheets[j].set_column(col, col, width)
            for col_num, value in enumerate(i.columns.values):
                (max_row, max_col) = i.shape
                writer.sheets[j].set_column(0, max_col - 1, 16)
                writer.sheets[j].write(0, 0, k, workbook.add_format({'bold': True, 'color': '#216d71', 'size': 14}))
                writer.sheets[j].write(1, 0, l, workbook.add_format({'bold': True, 'color': '#1b2b34', 'size': 12}))
        #       writer.sheets[j].add_table(0, 0, max_row, max_col - 1, {'columns': column_settings,'autofilter': True})
                writer.sheets[j].write(2, col_num, value, header_format)
        ## Write YTD Reports to .xlsx
                writer.sheets[j].autofilter(2,0,2,i.shape[1]-1)
        #        writer.sheets[j].freeze_panes(1,0)
        writer.save()
        writer.close()


