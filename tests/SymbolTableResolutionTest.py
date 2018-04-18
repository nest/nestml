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
import os
import unittest

from pynestml.meta_model.ASTSourceLocation import ASTSourceLocation
from pynestml.symbol_table.Scope import ScopeType
from pynestml.symbol_table.SymbolTable import SymbolTable
from pynestml.symbols.PredefinedFunctions import PredefinedFunctions
from pynestml.symbols.PredefinedTypes import PredefinedTypes
from pynestml.symbols.PredefinedUnits import PredefinedUnits
from pynestml.symbols.PredefinedVariables import PredefinedVariables
from pynestml.symbols.Symbol import SymbolKind
from pynestml.utils.Logger import Logger, LoggingLevel
from pynestml.utils.ModelParser import ModelParser

# minor setup steps required
Logger.init_logger(LoggingLevel.NO)
SymbolTable.initialize_symbol_table(ASTSourceLocation(start_line=0, start_column=0, end_line=0, end_column=0))
PredefinedUnits.register_units()
PredefinedTypes.register_types()
PredefinedVariables.register_variables()
PredefinedFunctions.register_functions()


class SymbolTableResolutionTest(unittest.TestCase):
    """
    This test is used to check if the resolution of symbols works as expected.
    """

    def test(self):
        model = ModelParser.parse_model(
            os.path.join(
                os.path.realpath(os.path.join(os.path.dirname(__file__), 'resources', 'ResolutionTest.nestml'))))
        scope = model.get_neuron_list()[0].get_scope()
        res1 = scope.resolve_to_all_scopes('test1', SymbolKind.VARIABLE)
        self.assertTrue(res1 is not None)
        res2 = scope.resolve_to_all_scopes('testNot', SymbolKind.VARIABLE)
        self.assertTrue(res2 is None)
        res3 = scope.resolve_to_all_scopes('test2', SymbolKind.VARIABLE)
        self.assertTrue(res3 is not None and res3.get_scope_type() == ScopeType.FUNCTION)
        res4 = scope.resolve_to_all_scopes('arg1', SymbolKind.VARIABLE)
        self.assertTrue(res4 is not None and res4.get_scope_type() == ScopeType.FUNCTION)
        res5 = scope.resolve_to_all_scopes('test3', SymbolKind.VARIABLE)
        self.assertTrue(res5 is not None and res5.get_scope_type() == ScopeType.FUNCTION)
        res6 = scope.resolve_to_all_scopes('test1', SymbolKind.FUNCTION)
        self.assertTrue(res6 is not None and res6.get_scope_type() == ScopeType.GLOBAL)
        res7 = scope.resolve_to_all_scopes('test6', SymbolKind.VARIABLE)
        self.assertTrue(res7 is not None and res7.get_scope_type() == ScopeType.UPDATE)


if __name__ == '__main__':
    unittest.main()
