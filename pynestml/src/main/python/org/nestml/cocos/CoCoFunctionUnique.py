#
# CoCoFunctionUnique.py
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


class CoCoFunctionUnique(CoCo):
    """
    This Coco ensures that each function is defined at most once per scope, thus no redeclaration occurs.
    """

    def checkCoCo(self, _neuron=None):
        """
        Checks if each function is defined at most once per scope.
        :param _neuron: a single neuron
        :type _neuron: ASTNeuron
        """
        from pynestml.src.main.python.org.nestml.symbol_table.Symbol import SymbolType
        for func in _neuron.getFunctions():
            symbols = _neuron.getScope().resolveToSymbol(func.getName(), SymbolType.FUNCTION)
            if isinstance(symbols, list) and len(symbols) > 1:
                raise VariableFunctionRedeclared('Function %s has been redeclared!' %func.getName() )


class VariableFunctionRedeclared(Exception):
    """
    This exception is thrown whenever a function has been re-defined in the model.
    """
    pass
