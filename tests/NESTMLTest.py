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

import os
import unittest

from pynestml.meta_model.ASTNestMLCompilationUnit import ASTNestMLCompilationUnit
from pynestml.meta_model.ASTSourceLocation import ASTSourceLocation
from pynestml.symbol_table.SymbolTable import SymbolTable
from pynestml.symbols.PredefinedFunctions import PredefinedFunctions
from pynestml.symbols.PredefinedTypes import PredefinedTypes
from pynestml.symbols.PredefinedUnits import PredefinedUnits
from pynestml.symbols.PredefinedVariables import PredefinedVariables
from pynestml.utils.Logger import LoggingLevel, Logger
from pynestml.utils.ModelParser import ModelParser

# setups the infrastructure
PredefinedUnits.register_units()
PredefinedTypes.register_types()
PredefinedFunctions.register_predefined_functions()
PredefinedVariables.register_predefined_variables()
SymbolTable.initialize_symbol_table(ASTSourceLocation(start_line=0, start_column=0, end_line=0, end_column=0))
Logger.init_logger(LoggingLevel.NO)


# TODO: this is not a unit test. Don't run it with unittests or use mocks to hide filesystem, solver etc
class NESTMLTest(unittest.TestCase):
    """
    Tests if the overall model processing frontend works as intended.
    """

    def test(self):
        for filename in os.listdir(os.path.realpath(os.path.join(os.path.dirname(__file__),
                                                                 os.path.join('..', 'models')))):
            if filename.endswith(".nestml"):
                # print('Start creating AST for ' + filename + ' ...'),
                model = ModelParser.parse_model(os.path.join(os.path.dirname(__file__),
                                                             os.path.join(os.path.join('..', 'models'), filename)))
                self.assertTrue(isinstance(model, ASTNestMLCompilationUnit))
        return


if __name__ == '__main__':
    unittest.main()
