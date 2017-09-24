#
# SymbolTableResolutionTest.py
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
from pynestml.src.main.python.org.nestml.parser.NESTMLParser import NESTMLParser
from pynestml.src.main.python.org.nestml.symbol_table.Scope import ScopeType
from pynestml.src.main.python.org.utils.Logger import Logger, LOGGING_LEVEL
from pynestml.src.main.python.org.nestml.symbol_table.predefined.PredefinedTypes import PredefinedTypes
from pynestml.src.main.python.org.nestml.symbol_table.predefined.PredefinedFunctions import PredefinedFunctions
from pynestml.src.main.python.org.nestml.symbol_table.predefined.PredefinedUnits import PredefinedUnits
from pynestml.src.main.python.org.nestml.symbol_table.predefined.PredefinedVariables import PredefinedVariables
from pynestml.src.main.python.org.nestml.symbol_table.SymbolTable import SymbolTable
from pynestml.src.main.python.org.nestml.ast.ASTSourcePosition import ASTSourcePosition
from pynestml.src.main.python.org.nestml.symbol_table.symbols.Symbol import SymbolKind
from pynestml.src.main.python.org.nestml.cocos.CoCosManager import CoCosManager

# minor setup steps required
Logger.initLogger(LOGGING_LEVEL.ERROR)
SymbolTable.initializeSymbolTable(ASTSourcePosition(_startLine=0, _startColumn=0, _endLine=0, _endColumn=0))
PredefinedUnits.registerUnits()
PredefinedTypes.registerTypes()
PredefinedVariables.registerPredefinedVariables()
PredefinedFunctions.registerPredefinedFunctions()
CoCosManager.initializeCoCosManager()

class SymbolTableResolutionTest(unittest.TestCase):
    """
    This test is used to check if the resolution of symbols works as expected.
    """
    def test(self):
        model = NESTMLParser.parseModel(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..',
                                                       'resources', 'ResolutionTest.nestml'))))
        scope = model.getNeuronList()[0].getScope()
        res1 = scope.resolveToAllScopes('test1',SymbolKind.VARIABLE)
        assert (res1 is not None)
        res2 = scope.resolveToAllScopes('testNot',SymbolKind.VARIABLE)
        assert (res2 is None)
        res3 = scope.resolveToAllScopes('test2',SymbolKind.VARIABLE)
        assert (res3 is not None and res3.getScopeType() == ScopeType.FUNCTION)
        res4 = scope.resolveToAllScopes('arg1',SymbolKind.VARIABLE)
        assert (res4 is not None and res4.getScopeType() == ScopeType.FUNCTION)
        res5 = scope.resolveToAllScopes('test3',SymbolKind.VARIABLE)
        assert (res5 is not None and res5.getScopeType() == ScopeType.FUNCTION)
        res6 = scope.resolveToAllScopes('test1',SymbolKind.FUNCTION)
        assert (res6 is not None and res6.getScopeType() == ScopeType.GLOBAL)
        res7 = scope.resolveToAllScopes('test6',SymbolKind.VARIABLE)
        assert (res7 is not None and res7.getScopeType() == ScopeType.UPDATE)
        return


if __name__ == '__main__':
    unittest.main()
