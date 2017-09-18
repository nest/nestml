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
    
        Attributes:
        __type      The type of this type symbol, i.e., buffer, variable or unit. Type: TypeSymbolType
    
    """
    __type = None

    def __init__(self, _elementReference=None, _scope=None, _name=None, _type=None):
        """
        Standard constructor.
        :param _elementReference: a reference to the first element where this type has been used/defined
        :type _elementReference: Object (or None, if predefined)
        :param _name: the name of the type symbol
        :type _name: str
        :param _type: the type of the type symbol
        :type _type: TypeSymbolType
        :param _scope: the scope in which this type is defined in 
        :type _scope: Scope
        """
        super(TypeSymbol, self).__init__(_elementReference=_elementReference, _scope=_scope, _name=_name)
        assert (_type is not None and isinstance(_type, TypeSymbolType)), \
            '(PyNestML.SymbolTable.TypeSymbol) No or wrong type of type provided!'
        self.__type = _type

    def getType(self):
        """
        Returns the type of this type symbol.
        :return: the type of this symbol
        :rtype: TypeSymbolType
        """
        return self.__type

    def printSymbol(self):
        """
        Returns a string representation of this symbol.
        :return: a string representation.
        :rtype: str
        """
        return 'TypeSymbol[' + self.getSymbolName() + ',' + str(self.getType()) + ']'

    def equals(self, _other=None):
        """
        Checks if the handed over type symbol object is equal to this (value-wise).
        :param _other: a type symbol object.
        :type _other: Symbol or subclass.
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        return type(self) != type(_other) and \
               self.getType() == _other.getType() and \
               self.getReferencedObject() == _other.getReferencedObject() and \
               self.getSymbolName() == _other.getSymbolName() and \
               self.getCorrespondingScope() == _other.getCorrespondingScope()

    @classmethod
    def getRealType(cls):
        """
        Returns a new type symbol of type real.
        :return: a new real symbol.
        :rtype: TypeSymbol
        """
        return cls(_name='real', _type=TypeSymbolType.PRIMITIVE)

    @classmethod
    def getVoidType(cls):
        """
        Returns a new type symbol of type void.
        :return: a new void symbol.
        :rtype: TypeSymbol
        """
        return cls(_name='void', _type=TypeSymbolType.PRIMITIVE)

    @classmethod
    def getBooleanType(cls):
        """
        Returns a new type symbol of type boolean.
        :return: a new boolean symbol.
        :rtype: TypeSymbol
        """
        return cls(_name='boolean', _type=TypeSymbolType.PRIMITIVE)

    @classmethod
    def getStringType(cls):
        """
        Returns a new type symbol of type string.
        :return: a new string symbol.
        :rtype: TypeSymbol 
        """
        return cls(_name='string', _type=TypeSymbolType.PRIMITIVE)

    @classmethod
    def getIntegerType(cls):
        """
        Returns a new type symbol of type integer.
        :return: a new integer symbol.
        :rtype: TypeSymbol
        """
        return cls(_name='integer', _type=TypeSymbolType.PRIMITIVE)


class TypeSymbolType(Enum):
    """
    This enum is used to represent the type of the type symbol.
    """
    UNIT = 1
    PRIMITIVE = 2
    BUFFER = 3
