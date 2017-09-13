"""
/*
 *  SymbolTableResolutionTest.py
 *
 *  This file is part of NEST.
 *
 *  Copyright (C) 2004 The NEST Initiative
 *
 *  NEST is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  NEST is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with NEST.  If not, see <http://www.gnu.org/licenses/>.
 *
 */
@author kperun
"""

from __future__ import print_function

import unittest
import os
from pynestml.src.main.python.org.nestml.parser.NESTMLParser import NESTMLParser
from pynestml.src.main.python.org.nestml.symbol_table.Symbol import SymbolType
from pynestml.src.main.python.org.nestml.symbol_table.Scope import ScopeType


class SymbolTableResolutionTest(unittest.TestCase):
    """
    This test is used to check if the resolution of symbols works as expected.
    """

    def test(self):
        model = NESTMLParser.parseModel(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), '..',
                                                       'resources', 'ResolutionTest.nestml'))))
        scope = model.getNeuronList()[0].getScope()
        res1 = scope.resolveToScope('test1', SymbolType.VARIABLE)
        assert (res1 is not None)
        res2 = scope.resolveToScope('testNot', SymbolType.VARIABLE)
        assert (res2 is None)
        res3 = scope.resolveToScope('test2', SymbolType.VARIABLE)
        assert (res3 is not None and res3.getScopeType() == ScopeType.FUNCTION)
        res4 = scope.resolveToScope('arg1', SymbolType.VARIABLE)
        assert (res4 is not None and res4.getScopeType() == ScopeType.FUNCTION)
        res5 = scope.resolveToScope('test3', SymbolType.VARIABLE)
        assert (res5 is not None and res5.getScopeType() == ScopeType.FUNCTION)
        res6 = scope.resolveToScope('test1', SymbolType.FUNCTION)
        assert (res6 is not None and res6.getScopeType() == ScopeType.GLOBAL)
        res7 = scope.resolveToScope('test6', SymbolType.VARIABLE)
        assert (res7 is not None and res7.getScopeType() == ScopeType.UPDATE)
        return


if __name__ == '__main__':
    unittest.main()
