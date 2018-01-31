# coding: utf-8
import logging


try:
    ascii
except NameError:
    # For Python 2
    def ascii(s):
        a = repr(s)
        if a.startswith(('u"', "u'")):
            a = a[1:]
        return a


class Worksheet(object):

    def __init__(self, sheet, is_xlsx=False):
        self.ws = sheet
        self.is_xlsx = is_xlsx

    def __getitem__(self, index):
        if self.is_xlsx:
            return self.ws[index]
        col = 0
        row = 0
        p = 1
        for i, char in enumerate(index.upper()):
            if char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                col += (ord(char) - ord('A')) * p
                p *= 26
            else:
                row = int(index[i:]) - 1
                break
        return self.ws.cell(row, col)

    @property
    def rows(self):
        if self.is_xlsx:
            return self.ws.rows
        nrows = self.ws.nrows
        return [self.ws.row(row) for row in range(nrows)]

    def get_value(self, col, row):
        return ascii(self.ws.col_values(col)[row])

    @property
    def name(self):
        return self.ws.name

    @property
    def title(self):
        return self.ws.name


class Cell(object):

    def __init__(self, value):
        self.value = value
