# coding: utf-8

import xlrd
import openpyxl

from .worksheet import Worksheet


class Workbook(object):
    def load(self, filename, **kwargs):
        """ Loads in an Excel file, using its extension to know the format """
        self.filename = filename
        if filename.endswith('.xlsx'):
            kwargs.pop('data_only', None)
            kwargs.pop('read_only', None)
            self.wb = openpyxl.load_workbook(filename, data_only=True, **kwargs)
        elif filename.endswith('.xls'):
            self.wb = xlrd.open_workbook(filename)
        else:
            raise Exception('Unknown format, please use either .xls or .xlsx')

    @property
    def is_xlsx(self):
        if not self.filename:
            raise NotImplementedError
        return self.filename.endswith('.xlsx')

    def get_sheet_names(self):
        if self.is_xlsx:
            return self.wb.get_sheet_names()
        return self.wb.sheet_names()

    def __getitem__(self, index):
        if self.is_xlsx:
            return self.wb[index]
        return Worksheet(self.wb.sheet_by_name(index))
