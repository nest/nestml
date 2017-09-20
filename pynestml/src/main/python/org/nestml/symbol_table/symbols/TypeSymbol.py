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
from pynestml.src.main.python.org.nestml.symbol_table.Scope import Scope


class TypeSymbol(Symbol):
    """
    This class is used to represent a single type symbol which represents the type of a element, e.g., a variable.
    
        Attributes:
        __unit              Stores an optional unit used to represent the type of this type symbol.
        __isInteger         Indicates whether it is an integer typed type symbol.
        __isReal            Indicates whether it is a real typed type symbol.
        __isVoid            Indicates whether it is a void typed type symbol.
        __isBoolean         Indicates whether it is a boolean typed type symbol.
        __isString          Indicates whether it is a string typed type symbol.
        __isBuffer          Indicates whether it is a buffer symbol.
    
    """
    __unit = None
    __isInteger = False
    __isReal = False
    __isVoid = False
    __isBoolean = False
    __isString = False
    __isBuffer = False

    def __init__(self, _elementReference=None, _scope=None, _name=None,
                 _unit=None, _isInteger=False, _isReal=False, _isVoid=False,
                 _isBoolean=False, _isString=False, _isBuffer=False):
        """
        Standard constructor.
        :param _elementReference: a reference to the first element where this type has been used/defined
        :type _elementReference: Object (or None, if predefined)
        :param _name: the name of the type symbol
        :type _name: str
        :param _scope: the scope in which this type is defined in 
        :type _scope: Scope
        :param _unit: a unit object.
        :type _unit: UnitType
        :param _isInteger: indicates whether this is an integer symbol type.
        :type _isInteger: bool
        :param _isReal: indicates whether this is a  real symbol type.
        :type _isReal: bool
        :param _isVoid: indicates whether this is a void symbol type.
        :type _isVoid: bool
        :param _isBoolean: indicates whether this is a boolean symbol type.
        :type _isBoolean: bool
        :param _isString: indicates whether this is a string symbol type.
        :type _isString: bool
        :param _isBuffer: indicates whether this symbol represents a buffer of a certain type, e.g. integer.
        """
        from pynestml.src.main.python.org.nestml.symbol_table.predefined.UnitType import UnitType
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.Symbol import SymbolType
        assert (_unit is None or isinstance(_unit, UnitType)), \
            '(PyNestML.SymbolTable.TypeSymbol) Wrong type of unit provided!'
        assert (isinstance(_isInteger, bool)), \
            '(PyNestML.SymbolTable.TypeSymbol) Wrong type of is-integer provided!'
        assert (isinstance(_isReal, bool)), \
            '(PyNestML.SymbolTable.TypeSymbol) Wrong type of is-real provided!'
        assert (isinstance(_isVoid, bool)), \
            '(PyNestML.SymbolTable.TypeSymbol) Wrong type of is-void provided'
        assert (isinstance(_isBoolean, bool)), \
            '(PyNestML.SymbolTable.TypeSymbol) Wrong type of is-boolean provided!'
        assert (isinstance(_isString, bool)), \
            '(PyNestML.SymbolTable.TypeSymbol) Wrong type of is-string provided!'
        assert (isinstance(_isBuffer, bool)), \
            '(PyNestML.SymbolTable.TypeSymbol) Wrong type of is-buffer provided!'
        assert (_unit is not None or _isInteger or _isReal or _isVoid or _isBoolean or _isString), \
            '(PyNestML.SymbolTable.TypeSymbol) Type of symbol not specified!'
        assert (_isInteger + _isReal + _isVoid + _isBoolean + _isString + (_unit is not None) == 1), \
            '(PyNestML.SymbolTable.TypeSymbol) Type of symbol over-specified!'
        super(TypeSymbol, self).__init__(_elementReference=_elementReference, _scope=_scope,
                                         _name=_name, _symbolType=SymbolType.TYPE)
        self.__unit = _unit
        self.__isInteger = _isInteger
        self.__isReal = _isReal
        self.__isVoid = _isVoid
        self.__isBoolean = _isBoolean
        self.__isString = _isString
        self.__isBuffer = _isBuffer

    def printSymbol(self):
        """
        Returns a string representation of this symbol.
        :return: a string representation.
        :rtype: str
        """
        elemType = ''
        if self.isInteger():
            elemType = 'integer'
        elif self.isReal():
            elemType = 'real'
        elif self.isVoid():
            elemType = 'void'
        elif self.isBoolean():
            elemType = 'boolean'
        elif self.isString():
            elemType = 'string'
        else:
            elemType = self.getUnit().printUnit()
        if self.isBuffer():
            elemType += ' buffer'
        return 'TypeSymbol[' + self.getSymbolName() + ',' + elemType + ']'

    def getUnit(self):
        """
        Returns the unit of this type symbol
        :return: a single unit object.
        :rtype: UnitType
        """
        return self.__unit

    def hasUnit(self):
        """
        Returns whether this type symbol's type is represented by a unit. 
        :return: True if unit, False otherwise.
        :rtype: bool
        """
        from pynestml.src.main.python.org.nestml.symbol_table.predefined.UnitType import UnitType
        return self.__unit is not None and isinstance(self.__unit, UnitType)

    def isInteger(self):
        """
        Indicates whether this is an integer typed symbol.
        :return: True if integer, otherwise False.
        :rtype: bool
        """
        return self.__isInteger

    def isReal(self):
        """
        Indicates whether this is a real typed symbol.
        :return: True if real, otherwise False.
        :rtype: bool
        """
        return self.__isReal

    def isVoid(self):
        """
        Indicates whether this is a real typed symbol.
        :return: True if void, otherwise False.
        :rtype: bool
        """
        return self.__isVoid

    def isBoolean(self):
        """
        Indicates whether this is a boolean typed symbol.
        :return: True if boolean, otherwise False.
        :rtype: bool
        """
        return self.__isBoolean

    def isString(self):
        """
        Indicates whether this is a string typed symbol.
        :return: True if string, otherwise False.
        :rtype: bool
        """
        return self.__isString

    def isBuffer(self):
        """
        Indicates whether this is a buffer symbol.
        :return: True if buffer, otherwise False.
        :rtype: bool
        """
        return self.__isBuffer

    def equals(self, _other=None):
        """
        Checks if the handed over type symbol object is equal to this (value-wise).
        :param _other: a type symbol object.
        :type _other: Symbol or subclass.
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        return type(self) != type(_other) and \
               self.isInteger() == _other.isInteger() and \
               self.isReal() == _other.isReal() and \
               self.isVoid() == _other.isVoid() and \
               self.isBoolean() == _other.isBoolean() and \
               self.isString() == _other.isString() and \
               self.isBuffer() == _other.isBuffer() and \
               (self.getUnit().equals(_other.getUnit()) if self.hasUnit() and _other.hasUnit() else True) and \
               self.getReferencedObject() == _other.getReferencedObject() and \
               self.getSymbolName() == _other.getSymbolName() and \
               self.getCorrespondingScope() == _other.getCorrespondingScope()
