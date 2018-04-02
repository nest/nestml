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
from pynestml.modelprocessor.Symbol import Symbol


class TypeSymbol(Symbol):
    """
    This class is used to represent a single type symbol which represents the type of a element, e.g., a variable.
    
        Attributes:
        unit              Stores an optional unit used to represent the type of this type symbol.
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

    def __init__(self, element_reference=None, scope=None, name=None,
                 unit=None, is_integer=False, is_real=False, is_void=False,
                 is_boolean=False, is_string=False, is_buffer=False):
        """
        Standard constructor.
        :param element_reference: a reference to the first element where this type has been used/defined
        :type element_reference: Object (or None, if predefined)
        :param name: the name of the type symbol
        :type name: str
        :param scope: the scope in which this type is defined in 
        :type scope: Scope
        :param unit: a unit object.
        :type unit: UnitType
        :param is_integer: indicates whether this is an integer symbol type.
        :type is_integer: bool
        :param is_real: indicates whether this is a  real symbol type.
        :type is_real: bool
        :param is_void: indicates whether this is a void symbol type.
        :type is_void: bool
        :param is_boolean: indicates whether this is a boolean symbol type.
        :type is_boolean: bool
        :param is_string: indicates whether this is a string symbol type.
        :type is_string: bool
        :param is_buffer: indicates whether this symbol represents a buffer of a certain type, e.g. integer.
        """
        from pynestml.modelprocessor.UnitType import UnitType
        from pynestml.modelprocessor.Symbol import SymbolKind
        assert (unit is None or isinstance(unit, UnitType)), \
            '(PyNestML.SymbolTable.TypeSymbol) Wrong type of unit provided (%s)!' % type(unit)
        assert (isinstance(is_integer, bool)), \
            '(PyNestML.SymbolTable.TypeSymbol) Wrong type of is-integer provided (%s)!' % type(is_integer)
        assert (isinstance(is_real, bool)), \
            '(PyNestML.SymbolTable.TypeSymbol) Wrong type of is-real provided (%s)!' % type(is_real)
        assert (isinstance(is_void, bool)), \
            '(PyNestML.SymbolTable.TypeSymbol) Wrong type of is-void provided (%s)!' % type(is_void)
        assert (isinstance(is_boolean, bool)), \
            '(PyNestML.SymbolTable.TypeSymbol) Wrong type of is-boolean provided (%s)!' % type(is_boolean)
        assert (isinstance(is_string, bool)), \
            '(PyNestML.SymbolTable.TypeSymbol) Wrong type of is-string provided (%s)!' % type(is_string)
        assert (isinstance(is_buffer, bool)), \
            '(PyNestML.SymbolTable.TypeSymbol) Wrong type of is-buffer provided (%s)!' % type(is_buffer)
        assert (unit is not None or is_integer or is_real or is_void or is_boolean or is_string), \
            '(PyNestML.SymbolTable.TypeSymbol) Type of symbol not specified!'
        assert (is_integer + is_real + is_void + is_boolean + is_string + (unit is not None) == 1), \
            '(PyNestML.SymbolTable.TypeSymbol) Type of symbol over-specified!'
        super(TypeSymbol, self).__init__(element_reference=element_reference, scope=scope,
                                         name=name, symbol_kind=SymbolKind.TYPE)
        self.__unit = unit
        self.__isInteger = is_integer
        self.__isReal = is_real
        self.__isVoid = is_void
        self.__isBoolean = is_boolean
        self.__isString = is_string
        self.__isBuffer = is_buffer
        return

    def print_symbol(self):
        """
        Returns a string representation of this symbol.
        :return: a string representation.
        :rtype: str
        """
        if self.is_integer():
            elem_type = 'integer'
        elif self.is_real():
            elem_type = 'real'
        elif self.is_void():
            elem_type = 'void'
        elif self.is_boolean():
            elem_type = 'boolean'
        elif self.is_string():
            elem_type = 'string'
        else:
            elem_type = self.get_unit().print_unit()
        if self.is_buffer():
            elem_type += ' buffer'
        return elem_type

    def get_unit(self):
        """
        Returns the unit of this type symbol
        :return: a single unit object.
        :rtype: UnitType
        """
        return self.__unit

    def is_unit(self):
        """
        Returns whether this type symbol's type is represented by a unit. 
        :return: True if unit, False otherwise.
        :rtype: bool
        """
        from pynestml.modelprocessor.UnitType import UnitType
        return self.__unit is not None and isinstance(self.__unit, UnitType)

    def get_encapsulated_unit(self):
        """
        Returns the sympy unit as encapsulated in the unit type object.
        :return: a single unit in the used type system: currently AstroPy.Units.
        :rtype: Symbol (AstroPy.Units)
        """
        return self.__unit.get_unit()

    def is_primitive(self):
        """
        Returns whether this symbol represents a primitive type.
        :return: true if primitive, otherwise false.
        :rtype: bool
        """
        return self.__isString or self.__isBoolean or self.__isVoid or self.__isReal or self.__isInteger

    def is_numeric(self):
        """
        Returns whether this symbol represents a numeric type.
        :return: True if numeric, otherwise False.
        :rtype: bool
        """
        return self.is_integer() or self.is_real() or self.is_unit()

    def is_numeric_primitive(self):
        """
        Returns whether this symbol represents a primitive numeric type, i.e., real or integer.
        :return: True if numeric primitive, otherwise False.
        :rtype: bool
        """
        return self.is_integer() or self.is_real()

    def is_integer(self):
        """
        Indicates whether this is an integer typed symbol.
        :return: True if integer, otherwise False.
        :rtype: bool
        """
        return self.__isInteger

    def is_real(self):
        """
        Indicates whether this is a real typed symbol.
        :return: True if real, otherwise False.
        :rtype: bool
        """
        return self.__isReal

    def is_void(self):
        """
        Indicates whether this is a real typed symbol.
        :return: True if void, otherwise False.
        :rtype: bool
        """
        return self.__isVoid

    def is_boolean(self):
        """
        Indicates whether this is a boolean typed symbol.
        :return: True if boolean, otherwise False.
        :rtype: bool
        """
        return self.__isBoolean

    def is_string(self):
        """
        Indicates whether this is a string typed symbol.
        :return: True if string, otherwise False.
        :rtype: bool
        """
        return self.__isString

    def is_buffer(self):
        """
        Indicates whether this is a buffer symbol.
        :return: True if buffer, otherwise False.
        :rtype: bool
        """
        return self.__isBuffer

    def set_buffer(self, is_buffer):
        """
        Indicates whether this is a buffer object or not.
        :param is_buffer: True if object shall be buffer, otherwise False.
        :type is_buffer: bool
        """
        self.__isBuffer = is_buffer
        return

    def equals(self, other):
        """
        Checks if the handed over type symbol object is equal to this (value-wise).
        :param other: a type symbol object.
        :type other: Symbol or subclass.
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if not isinstance(other, TypeSymbol):
            return False

        # deferr comparison of units to sympy library
        if self.is_unit() and other.is_unit():
            self_unit = self.get_encapsulated_unit()
            other_unit = other.get_encapsulated_unit()
            return self_unit == other_unit

        return (self.is_integer() == other.is_integer() and
                self.is_real() == other.is_real() and
                self.is_void() == other.is_void() and
                self.is_boolean() == other.is_boolean() and
                self.is_string() == other.is_string() and
                self.is_buffer() == other.is_buffer() and
                (self.get_unit().equals(other.get_unit()) if self.is_unit() and other.is_unit() else True) and
                self.get_referenced_object() == other.get_referenced_object() and
                self.get_symbol_name() == other.get_symbol_name() and
                self.get_corresponding_scope() == other.get_corresponding_scope())
