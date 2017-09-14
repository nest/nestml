#
# CoCoVariableOncePerScope.py
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
from pynestml.src.main.python.org.nestml.cocos.CoCo import CoCo


class CoCoVariableOncePerScope(CoCo):
    """
    This coco ensures that each variables is defined at most once per scope, thus no redeclaration occurs.
    """

    def checkCoCo(self, _neuron=None):
        """
        Checks if each variable is defined at most once per scope. Obviously, this test does not check if a declaration
        is shadowed by an embedded scope.
        :param _neuron: a single neuron
        :type _neuron: ASTNeuron
        """
        self.__checkScope(_neuron.getScope())

    def __checkScope(self, _scope=None):
        """
        Private method: checks if a symbol has been declared more then one time per scope. Recursively it checks its 
        sub-scopes.
        :param _scope: a single scope element
        :type _scope: Scope
        """
        from pynestml.src.main.python.org.nestml.symbol_table.Scope import Scope
        assert (_scope is not None and isinstance(_scope, Scope)), \
            '(PyNestML.CoCo) No or wrong type of scope provided!'
        for sym1 in _scope.getSymbolsInThisScope():  # TODO: in o(n^2), maybe a better is solution possible
            for sym2 in _scope.getSymbolsInThisScope():
                if sym1 is not sym2 and sym1.getSymbolName() == sym2.getSymbolName() and \
                                sym1.getSymbolType() == sym2.getSymbolType():
                    raise VariableRedeclaredInSameScopeException('Variable %s redeclared!' % sym1.getSymbolName())
        for scope in _scope.getScopes():
            self.__checkScope(scope)


class VariableRedeclaredInSameScopeException(Exception):
    """
    This exception is thrown whenever a variable has been re-declared in the same scope.
    """
    pass
