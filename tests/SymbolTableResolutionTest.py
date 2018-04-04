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
from pynestml.modelprocessor.ModelParser import ModelParser
from pynestml.modelprocessor.Scope import ScopeType
from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes
from pynestml.modelprocessor.PredefinedFunctions import PredefinedFunctions
from pynestml.modelprocessor.PredefinedUnits import PredefinedUnits
from pynestml.modelprocessor.PredefinedVariables import PredefinedVariables
from pynestml.modelprocessor.SymbolTable import SymbolTable
from pynestml.modelprocessor.ASTSourceLocation import ASTSourceLocation
from pynestml.modelprocessor.Symbol import SymbolKind
from pynestml.utils.Logger import Logger, LoggingLevel

# minor setup steps required
Logger.init_logger(LoggingLevel.NO)
SymbolTable.initialize_symbol_table(ASTSourceLocation(start_line=0, start_column=0, end_line=0, end_column=0))
PredefinedUnits.register_units()
PredefinedTypes.register_types()
PredefinedVariables.register_predefined_variables()
PredefinedFunctions.register_predefined_functions()


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
        assert (res1 is not None)
        res2 = scope.resolve_to_all_scopes('testNot', SymbolKind.VARIABLE)
        assert (res2 is None)
        res3 = scope.resolve_to_all_scopes('test2', SymbolKind.VARIABLE)
        assert (res3 is not None and res3.get_scope_type() == ScopeType.FUNCTION)
        res4 = scope.resolve_to_all_scopes('arg1', SymbolKind.VARIABLE)
        assert (res4 is not None and res4.get_scope_type() == ScopeType.FUNCTION)
        res5 = scope.resolve_to_all_scopes('test3', SymbolKind.VARIABLE)
        assert (res5 is not None and res5.get_scope_type() == ScopeType.FUNCTION)
        res6 = scope.resolve_to_all_scopes('test1', SymbolKind.FUNCTION)
        assert (res6 is not None and res6.get_scope_type() == ScopeType.GLOBAL)
        res7 = scope.resolve_to_all_scopes('test6', SymbolKind.VARIABLE)
        assert (res7 is not None and res7.get_scope_type() == ScopeType.UPDATE)
        return


if __name__ == '__main__':
    unittest.main()
