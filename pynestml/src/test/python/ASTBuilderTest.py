"""
@author kperun
TODO header
"""

import unittest
import os
from pynestml.src.main.python.org.nestml.parser.NESTMLParser import NESTMLParser


class MyTestCase(unittest.TestCase):
    def test(self):
        for filename in os.listdir(os.path.join('..', '..', '..', '..', 'models')):
            if filename.endswith(".nestml"):
                print("Start parsing " + filename + " ... ", end=''),
                NESTMLParser.parseModel('../../../../models' + filename)
                print("done")


if __name__ == '__main__':
    unittest.main()
