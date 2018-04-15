#
# ExpressionTypeCalculationTest.py
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
import os
import unittest

from pynestml.modelprocessor.ASTSourceLocation import ASTSourceLocation
from pynestml.modelprocessor.ASTVisitor import ASTVisitor
from pynestml.modelprocessor.ModelParser import ModelParser
from pynestml.modelprocessor.PredefinedFunctions import PredefinedFunctions
from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes
from pynestml.modelprocessor.PredefinedUnits import PredefinedUnits
from pynestml.modelprocessor.PredefinedVariables import PredefinedVariables
from pynestml.modelprocessor.SymbolTable import SymbolTable
from pynestml.utils.Logger import Logger, LoggingLevel

# minor setup steps required
SymbolTable.initialize_symbol_table(ASTSourceLocation(start_line=0, start_column=0, end_line=0, end_column=0))
PredefinedUnits.register_units()
PredefinedTypes.register_types()
PredefinedVariables.register_predefined_variables()
PredefinedFunctions.register_predefined_functions()


class ExpressionTestVisitor(ASTVisitor):
    def end_visit_assignment(self, node):
        return

    def end_visit_expression(self, node):
        return


class MagnitudeCompatibilityTest(unittest.TestCase):
    """
    A simple test that prints all top-level expression types in a file.
    """

    def test(self):
        # Todo: this test is not yet complete
        Logger.init_logger(LoggingLevel.NO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__),
                                                       'resources', 'MagnitudeCompatibilityTest.nestml'))))
        # Logger.setCurrentNeuron(model.getNeuronList()[0])
        ExpressionTestVisitor().handle(model)
        # Logger.setCurrentNeuron(None)
        # assert (len(Logger.getAllMessagesOfLevelAndOrNeuron(model.getNeuronList()[0], LOGGING_LEVEL.ERROR)) == 2)


if __name__ == '__main__':
    unittest.main()
