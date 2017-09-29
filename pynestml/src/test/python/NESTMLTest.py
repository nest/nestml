#
# NESTMLTest.py
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
from pynestml.src.main.python.org.nestml.symbol_table.predefined.PredefinedTypes import PredefinedTypes
from pynestml.src.main.python.org.nestml.symbol_table.predefined.PredefinedUnits import PredefinedUnits
from pynestml.src.main.python.org.nestml.symbol_table.predefined.PredefinedFunctions import PredefinedFunctions
from pynestml.src.main.python.org.nestml.symbol_table.predefined.PredefinedVariables import PredefinedVariables
from pynestml.src.main.python.org.utils.Logger import LOGGING_LEVEL, Logger
from pynestml.src.main.python.org.nestml.cocos.CoCosManager import CoCosManager
from pynestml.src.main.python.org.nestml.ast.ASTSourcePosition import ASTSourcePosition
from pynestml.src.main.python.org.nestml.symbol_table.SymbolTable import SymbolTable

# setups the infrastructure
PredefinedUnits.registerUnits()
PredefinedTypes.registerTypes()
PredefinedFunctions.registerPredefinedFunctions()
PredefinedVariables.registerPredefinedVariables()
SymbolTable.initializeSymbolTable(ASTSourcePosition(_startLine=0, _startColumn=0, _endLine=0, _endColumn=0))
Logger.initLogger(LOGGING_LEVEL.NO)
CoCosManager.initializeCoCosManager()


class NESTMLTest(unittest.TestCase):
    """
    Tests if the overall model processing frontend works as intended.
    """

    def test(self):
        for filename in os.listdir(os.path.realpath(os.path.join(os.path.dirname(__file__),
                                                                 os.path.join('..', '..', '..', '..', 'models')))):
            if filename.endswith(".nestml"):
                # print('Start creating AST for ' + filename + ' ...'),
                NESTMLParser.parseModel(os.path.join(os.path.dirname(__file__),
                                                     os.path.join(os.path.join('..', '..', '..', '..',
                                                                               'models'), filename)))
        return


if __name__ == '__main__':
    unittest.main()
