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

from pynestml.codegeneration.UnitConverter import UnitConverter
from pynestml.modelprocessor.ASTVisitor import ASTVisitor
from pynestml.modelprocessor.ModelParser import ModelParser
from pynestml.modelprocessor.PredefinedFunctions import PredefinedFunctions
from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes
from pynestml.modelprocessor.PredefinedUnits import PredefinedUnits
from pynestml.modelprocessor.PredefinedVariables import PredefinedVariables
from pynestml.modelprocessor.Symbol import SymbolKind
from pynestml.modelprocessor.SymbolTable import SymbolTable
from pynestml.modelprocessor.UnitTypeSymbol import UnitTypeSymbol
from pynestml.utils.Logger import Logger, LoggingLevel
from pynestml.utils.Messages import MessageCode

# minor setup steps required
SymbolTable.initialize_symbol_table(ASTSourceLocation(start_line=0, start_column=0, end_line=0, end_column=0))
PredefinedUnits.register_units()
PredefinedTypes.register_types()
PredefinedVariables.register_predefined_variables()
PredefinedFunctions.register_predefined_functions()


class ExpressionTestVisitor(ASTVisitor):
    def end_visit_assignment(self, node):
        scope = node.getScope()
        var_name = node.getVariable().getName()

        _expr = node.getExpression()

        var_symbol = scope.resolveToSymbol(var_name, SymbolKind.VARIABLE)

        _equals = var_symbol.getTypeSymbol().equals(_expr.type)

        message = 'line ' + str(_expr.getSourcePosition()) + ' : LHS = ' + \
                  var_symbol.getTypeSymbol().getSymbolName() + \
                  ' RHS = ' + _expr.type.getSymbolName() + \
                  ' Equal ? ' + str(_equals)

        if isinstance(_expr.type, UnitTypeSymbol):
            message += " Neuroscience Factor: " + \
                       str(UnitConverter().getFactor(_expr.type.astropy_unit))

        Logger.log_message(error_position=node.get_source_position(), code=MessageCode.TYPE_MISMATCH,
                           message=message, log_level=LoggingLevel.INFO)

        if _equals is False:
            Logger.log_message(message="Type mismatch in test!",
                               code=MessageCode.TYPE_MISMATCH,
                               error_position=node.get_source_position(),
                               log_level=LoggingLevel.ERROR)
        return


class ExpressionTypeCalculationTest(unittest.TestCase):
    """
    A simple test that prints all top-level expression types in a file.
    """

    # TODO: this test needs to be refactored.
    def test(self):
        Logger.init_logger(LoggingLevel.INFO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__),
                                                       'resources', 'ExpressionTypeTest.nestml'))))
        Logger.set_current_neuron(model.get_neuron_list()[0])
        model.accept(ExpressionTestVisitor())
        # ExpressionTestVisitor().handle(model)
        Logger.set_current_neuron(None)
        self.assertEqual(len(Logger.get_all_messages_of_level_and_or_neuron(model.get_neuron_list()[0],
                                                                            LoggingLevel.ERROR)), 2)


if __name__ == '__main__':
    unittest.main()
