"""
@author kperun
TODO header
"""
from __future__ import print_function

import unittest
import os
from pynestml.src.main.python.org.nestml.parser.NESTMLParser import NESTMLParser


class ASTBuildingTest(unittest.TestCase):
    def test(self):
        for filename in os.listdir(os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'resources'))):
            if filename.endswith(".nestml"):
                NESTMLParser.parseModel(
                    os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'resources')),
                                 filename))


if __name__ == '__main__':
    unittest.main()
