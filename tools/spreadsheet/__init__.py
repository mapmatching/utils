# coding: utf-8

from .workbook import Workbook


def load_workbook(filename, **kwargs):  # openpyxl syntax
    wb = Workbook()
    wb.load(filename, **kwargs)
    return wb


def open_workbook(filename, **kwargs):  # xlrd syntax
    return load_workbook(filename, **kwargs)
