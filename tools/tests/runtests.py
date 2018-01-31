# coding=utf-8
"""db package

include:
    SQLAlchemy -> sqlalchemy
    Redis -> redis
"""
# 待完成:
# Mongodb -> mongodb
# Fastdfs -> fastdfs

from __future__ import absolute_import, division, print_function, with_statement

__author__ = "Yihang Yang"
__copyright__ = "Copyright 2015, Kanjian"
__credits__ = ["Yihang Yang"]
__license__ = "Apache"
__version__ = "2.0"
__maintainer__ = "Yihang Yang"
__email__ = "lianghuihui@kanjian.com"
__status__ = "Production"


import unittest

from tornado.options import parse_command_line
try:
    from colour_runner.runner import ColourTextTestRunner as TextTestRunner
except ImportError:
    from unittest import TextTestRunner

parse_command_line()

TEST_MODULES = [
    "tools.error.doctests",
    "tools.kanjian_email.doctests",
]


def main():
    """main test function"""
    suite = unittest.TestSuite()
    for case in unittest.defaultTestLoader.loadTestsFromNames(TEST_MODULES):
        suite.addTests(case)
    TextTestRunner(verbosity=2).run(suite)


if __name__ == "__main__":
    main()
