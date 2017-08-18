"""
@author kperun
TODO header
"""
import os

import unittest


def PyNESTMLTestSuite():
    test_loader = unittest.TestLoader()
    print(os.path.dirname(__file__))
    test_suite = test_loader.discover(os.path.dirname(__file__), pattern='*Test.py')
    return test_suite
