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
from pynestml.nestml.NESTMLParser import NESTMLParser
from pynestml.nestml.Symbol import SymbolKind
from pynestml.nestml.NESTMLVisitor import NESTMLVisitor
from pynestml.nestml.PredefinedTypes import PredefinedTypes
from pynestml.nestml.PredefinedFunctions import PredefinedFunctions
from pynestml.nestml.PredefinedUnits import PredefinedUnits
from pynestml.nestml.PredefinedVariables import PredefinedVariables
from pynestml.nestml.SymbolTable import SymbolTable
from pynestml.nestml.ASTSourcePosition import ASTSourcePosition
from pynestml.nestml.CoCosManager import CoCosManager
from pynestml.utils.Logger import Logger, LOGGING_LEVEL

# minor setup steps required
SymbolTable.initializeSymbolTable(ASTSourcePosition(_startLine=0, _startColumn=0, _endLine=0, _endColumn=0))
PredefinedUnits.registerUnits()
PredefinedTypes.registerTypes()
PredefinedVariables.registerPredefinedVariables()
PredefinedFunctions.registerPredefinedFunctions()
CoCosManager.initializeCoCosManager()


class expressionTestVisitor(NESTMLVisitor):
    def endvisitAssignment(self, _assignment=None):
        scope = _assignment.getScope()
        varName = _assignment.getVariable().getName()

        _expr = _assignment.getExpression()

        varSymbol = scope.resolveToSymbol(varName, SymbolKind.VARIABLE)

        _equals = varSymbol.getTypeSymbol().equals(_expr.getTypeEither().getValue())

        Logger.logMessage('line ' + _expr.getSourcePosition().printSourcePosition() + ' : LHS = ' +
                          varSymbol.getTypeSymbol().getSymbolName() + ' RHS = ' +
                          _expr.getTypeEither().getValue().getSymbolName() +
                          ' Equal ? ' + str(_equals), LOGGING_LEVEL.INFO)

        if _equals is False:
            Logger.logMessage("Type mismatch in test!", LOGGING_LEVEL.ERROR)
        return


class ExpressionTypeCalculationTest(unittest.TestCase):
    """
    A simple test that prints all top-level expression types in a file
    """

    def test(self):
        Logger.initLogger(LOGGING_LEVEL.NO)
        model = NESTMLParser.parseModel(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__),
                                                       'resources', 'ExpressionTypeTest.nestml'))))
        expressionTestVisitor().handle(model)
        assert (len(Logger.getAllMessagesOfLevelAndOrNeuron(None, LOGGING_LEVEL.ERROR)) == 2)


if __name__ == '__main__':
    unittest.main()
