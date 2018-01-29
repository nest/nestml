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

from pynestml.modelprocessor.ModelVisitor import NESTMLVisitor

from pynestml.modelprocessor.ModelParser import ModelParser

from pynestml.codegeneration.UnitConverter import UnitConverter
from pynestml.generated.PyNESTMLParser import PyNESTMLParser
from pynestml.generated.PyNESTMLVisitor import PyNESTMLVisitor
from pynestml.modelprocessor.Symbol import SymbolKind
from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes
from pynestml.modelprocessor.PredefinedFunctions import PredefinedFunctions
from pynestml.modelprocessor.PredefinedUnits import PredefinedUnits
from pynestml.modelprocessor.PredefinedVariables import PredefinedVariables
from pynestml.modelprocessor.SymbolTable import SymbolTable
from pynestml.modelprocessor.ASTSourcePosition import ASTSourcePosition
from pynestml.modelprocessor.CoCosManager import CoCosManager
from pynestml.utils.Logger import Logger, LOGGING_LEVEL
from pynestml.utils.Messages import MessageCode

# minor setup steps required
SymbolTable.initializeSymbolTable(ASTSourcePosition(_startLine=0, _startColumn=0, _endLine=0, _endColumn=0))
PredefinedUnits.registerUnits()
PredefinedTypes.registerTypes()
PredefinedVariables.registerPredefinedVariables()
PredefinedFunctions.registerPredefinedFunctions()



class ExpressionTestVisitor(NESTMLVisitor):
    def endvisitAssignment(self, _assignment=None):

        return

    def endvisitExpression(self, _expr=None):
        return


class MagnitudeCompatibilityTest(unittest.TestCase):
    """
    A simple test that prints all top-level expression types in a file.
    """
    def test(self):
        Logger.initLogger(LOGGING_LEVEL.INFO)
        model = ModelParser.parseModel(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__),
                                                       'resources', 'MagnitudeCompatibilityTest.nestml'))))
        Logger.setCurrentNeuron(model.getNeuronList()[0])
        ExpressionTestVisitor().handle(model)
        Logger.setCurrentNeuron(None)
        #assert (len(Logger.getAll°MessagesOfLevelAndOrNeuron(model.getNeuronList()[0], LOGGING_LEVEL.ERROR)) == 2)


if __name__ == '__main__':
    unittest.main()
