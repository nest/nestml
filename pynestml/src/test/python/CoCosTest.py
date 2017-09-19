#
# CoCosTest.py
#
# This file is part of NEST.
#
# Copyright (C) 2004 The NEST Initiative
#
# NEST is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# NEST is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NEST.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function

import unittest
import os
from pynestml.src.main.python.org.nestml.parser.NESTMLParser import NESTMLParser
from pynestml.src.main.python.org.nestml.cocos.CoCoElementDefined import ElementNotDefined
from pynestml.src.main.python.org.nestml.cocos.CoCoEachBlockUnique import BlockNotUniqueException


class ElementInSameLine(unittest.TestCase):
    def test(self):
        print('Test ' + str(type(self)) + ' not active!')
        return
        try:
            model = NESTMLParser.parseModel(
                os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'resources')),
                             'CoCoElementInSameLine.nestml'))
        except ElementNotDefined:
            return
        return 1  # meaning an error


class ElementNotDefinedInScope(unittest.TestCase):
    def test(self):
        print('Test ' + str(type(self)) + ' not active!')
        return
        try:
            model = NESTMLParser.parseModel(
                os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'resources')),
                             'CoCoElementNotDefined.nestml'))
        except ElementNotDefined:
            return
        return 1  # meaning an error


class EachBlockUnique(unittest.TestCase):
    def test(self):
        print('Test ' + str(type(self)) + ' not active!' )
        return
        try:
            model = NESTMLParser.parseModel(
                os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'resources')),
                             'CoCoEachBlockUnique.nestml'))
        except BlockNotUniqueException:
            return
        return 1  # meaning an error


if __name__ == '__main__':
    unittest.main()
