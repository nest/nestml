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
import unittest
import os

from pynestml.codegeneration.UnitConverter import UnitConverter
from pynestml.modelprocessor.ModelParser import ModelParser
from pynestml.modelprocessor.Symbol import SymbolKind
from pynestml.modelprocessor.ASTVisitor import ASTVisitor
from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes
from pynestml.modelprocessor.PredefinedFunctions import PredefinedFunctions
from pynestml.modelprocessor.PredefinedUnits import PredefinedUnits
from pynestml.modelprocessor.PredefinedVariables import PredefinedVariables
from pynestml.modelprocessor.SymbolTable import SymbolTable
from pynestml.modelprocessor.ASTSourcePosition import ASTSourcePosition
from pynestml.utils.Logger import Logger, LOGGING_LEVEL
from pynestml.utils.Messages import MessageCode

# minor setup steps required
SymbolTable.initializeSymbolTable(ASTSourcePosition(_startLine=0, _startColumn=0, _endLine=0, _endColumn=0))
PredefinedUnits.registerUnits()
PredefinedTypes.registerTypes()
PredefinedVariables.registerPredefinedVariables()
PredefinedFunctions.registerPredefinedFunctions()


class expressionTestVisitor(ASTVisitor):
    def endvisit_assignment(self, node=None):
        scope = node.get_scope()
        var_name = node.lhs.get_name()

        _expr = node.get_expression()

        var_symbol = scope.resolveToSymbol(var_name, SymbolKind.VARIABLE)

        _equals = var_symbol.get_type_symbol().equals(_expr.get_type_either().getValue())

        message = 'line ' + str(_expr.get_source_position()) + ' : LHS = ' + \
                  var_symbol.get_type_symbol().get_symbol_name() + \
                  ' RHS = ' + _expr.get_type_either().getValue().get_symbol_name() + \
                  ' Equal ? ' + str(_equals)

        if _expr.get_type_either().getValue().is_unit():
            message += (" Neuroscience Factor: " +
                        str(UnitConverter().getFactor(_expr.get_type_either().getValue().get_unit().get_unit())))

        Logger.logMessage(_errorPosition=node.get_source_position(), _code=MessageCode.TYPE_MISMATCH,
                          _message=message, _logLevel=LOGGING_LEVEL.INFO)

        if _equals is False:
            Logger.logMessage(_message="Type mismatch in test!",
                              _code=MessageCode.TYPE_MISMATCH,
                              _errorPosition=node.get_source_position(),
                              _logLevel=LOGGING_LEVEL.ERROR)
        return


class ExpressionTypeCalculationTest(unittest.TestCase):
    """
    A simple test that prints all top-level rhs types in a file.
    """

    def test(self):
        Logger.initLogger(LOGGING_LEVEL.NO)
        model = ModelParser.parse_model(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__),
                                                       'resources', 'ExpressionTypeTest.nestml'))))
        Logger.setCurrentNeuron(model.get_neuron_list()[0])
        expressionTestVisitor().handle(model)
        Logger.setCurrentNeuron(None)
        assert (len(Logger.getAllMessagesOfLevelAndOrNeuron(model.get_neuron_list()[0], LOGGING_LEVEL.ERROR)) == 2)


if __name__ == '__main__':
    unittest.main()
