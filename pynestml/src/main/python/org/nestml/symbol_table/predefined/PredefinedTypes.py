#
# PredefinedTypes.py
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
from pynestml.src.main.python.org.nestml.symbol_table.Scope import Scope
from pynestml.src.main.python.org.nestml.symbol_table.Scope import ScopeType
from pynestml.src.main.python.org.nestml.symbol_table.symbols.TypeSymbol import TypeSymbol
from pynestml.src.main.python.org.nestml.symbol_table.symbols.TypeSymbol import TypeSymbolType


class PredefinedTypes:
    """
    This class represents all types which are predefined in the system.
    
    Attributes:
        __name2type     A dict from names of variables to the corresponding type symbols.
    
    """
    __name2type = {}
    __REAL_TYPE = 'real'
    __VOID_TYPE = 'void'
    __BOOLEAN_TYPE = 'boolean'
    __STRING_TYPE = 'string'
    __INTEGER_TYPE = 'integer'

    @classmethod
    def registerPrimitiveTypes(cls):
        """
        Adds a set of primitive data types to the handed over scope. It assures that those types are valid and can
        be used.
        """
        cls.__registerReal()
        cls.__registerVoid()
        cls.__registerBoolean()
        cls.__registerString()
        cls.__registerInteger()
        return

    @classmethod
    def __registerReal(cls):
        """
        Adds the real type symbol to the dict of predefined types.
        """
        symbol = TypeSymbol(_name=cls.__REAL_TYPE, _type=TypeSymbolType.PRIMITIVE)
        cls.__name2type[cls.__REAL_TYPE] = symbol
        return

    @classmethod
    def __registerVoid(cls):
        """
        Adds the void type to the dict of predefined types.
        """
        symbol = TypeSymbol(_name='void', _type=TypeSymbolType.PRIMITIVE)
        cls.__name2type[cls.__VOID_TYPE] = symbol
        return

    @classmethod
    def __registerBoolean(cls):
        """
        Adds the boolean type to the dict of predefined types.
        """
        symbol = TypeSymbol(_name='boolean', _type=TypeSymbolType.PRIMITIVE)
        cls.__name2type[cls.__BOOLEAN_TYPE] = symbol
        return

    @classmethod
    def __registerString(cls):
        """
        Adds the string type to the dict of predefined types.
        """
        symbol = TypeSymbol(_name='string', _type=TypeSymbolType.PRIMITIVE)
        cls.__name2type[cls.__STRING_TYPE] = symbol
        return

    @classmethod
    def __registerInteger(cls):
        """
        Adds the integer type to the dict of predefined types.
        """
        symbol = TypeSymbol(_name='integer', _type=TypeSymbolType.PRIMITIVE)
        cls.__name2type[cls.__INTEGER_TYPE] = symbol
        return

    """
    TODO: registerBufferTypes
          getTypes
          getType
          getTypeIfExists
    """
