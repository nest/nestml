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
from pynestml.utils.Messages import MessageCode

# minor setup steps required
SymbolTable.initializeSymbolTable(ASTSourcePosition(_startLine=0, _startColumn=0, _endLine=0, _endColumn=0))
PredefinedUnits.registerUnits()
PredefinedTypes.registerTypes()
PredefinedVariables.registerPredefinedVariables()
PredefinedFunctions.registerPredefinedFunctions()
CoCosManager.initializeCoCosManager()


class expressionTestVisitor(NESTMLVisitor):
    def endvisitAssignment(self, _assignment=None):

        return

    def endvisitExpression(self, _expr=None):
        lhsTypeE = _expr.getLhs().getTypeEither()
        rhsTypeE = _expr.getRhs().getTypeEither()

        lhsType = lhsTypeE.getValue()
        rhsType = rhsTypeE.getValue()

        if _expr.isPlusOp():
            Logger.logMessage(_message="Lhs: " + lhsType.printSymbol() + " Rhs: " + rhsType.printSymbol(),
                          _code=MessageCode.DRY_RUN,
                          _errorPosition=_expr.getSourcePosition(),
                          _logLevel=LOGGING_LEVEL.INFO)
        return


class ExpressionTypeCalculationTest(unittest.TestCase):
    """
    A simple test that prints all top-level expression types in a file.
    """
    def test(self):
        Logger.initLogger(LOGGING_LEVEL.INFO)
        model = NESTMLParser.parseModel(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__),
                                                       'resources', 'MagnitudeCompatibilityTest.nestml'))))
        Logger.setCurrentNeuron(model.getNeuronList()[0])
        expressionTestVisitor().handle(model)
        Logger.setCurrentNeuron(None)
        #assert (len(Logger.getAllMessagesOfLevelAndOrNeuron(model.getNeuronList()[0], LOGGING_LEVEL.ERROR)) == 2)


if __name__ == '__main__':
    unittest.main()
