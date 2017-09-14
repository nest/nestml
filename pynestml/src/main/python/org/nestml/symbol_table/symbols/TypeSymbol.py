#
# TypeSymbol.py
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
from enum import Enum
from pynestml.src.main.python.org.nestml.symbol_table.symbols.Symbol import Symbol
from pynestml.src.main.python.org.nestml.symbol_table.symbols.Symbol import SymbolType
from pynestml.src.main.python.org.nestml.symbol_table.Scope import Scope


class TypeSymbol(Symbol):
    """
    This class is used to represent a single type symbol which represents the type of a element, e.g., a variable.
    """
    __name = None
    __type = None

    def __init__(self, _name=None, _typeType=None, _scope=None):
        """
        Standard constructor.
        :param _name: the name of the type symbol
        :type _name: str
        :param _typeType: the type of the type symbol
        :type _typeType: TypeSymbolType
        :param _scope: the scope in which this type is defined in 
        :type _scope: Scope
        """
        super(Symbol, self).__init__(_elementReference=None, _scope=_scope, _type=SymbolType.TYPE, _name=_name)
        assert (_typeType is not None and isinstance(_typeType, TypeSymbolType)), \
            '(PyNestML.SymbolTable.TypeSymbol) No or wrong type of type-type provided!'
        self.__type = _typeType

    def getType(self):
        """
        Returns the type of this type symbol.
        :return: the type of this symbol
        :rtype: TypeSymbolType
        """
        return self.__type


class TypeSymbolType(Enum):
    """
    This enum is used to represent the type of the type symbol.
    """
    UNIT = 1
    PRIMITIVE = 2
    BUFFER = 3
