#
# ASTDataType.py
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

from pynestml.meta_model.ASTNode import ASTNode


class ASTDataType(ASTNode):
    """
    A datatype class as used to store a datatype of an element.
    ASTDataType. Represents predefined datatypes and gives a possibility to use an unit
    datatype.
    @attribute boolean getters for integer, real, ...
    @attribute unitType a SI datatype
    datatype : 'integer'
               | 'real'
               | 'string'
               | 'boolean'
               | 'void'
               | unitType;
    """
    __isInteger = False
    __isReal = False
    __isString = False
    __isBoolean = False
    __isVoid = False
    __isUnitType = None  # a unit type is not a boolean, but a concrete object
    __typeSymbol = None  # the corresponding type symbol

    def __init__(self, is_integer=False, is_real=False, is_string=False, is_boolean=False, is_void=False,
                 is_unit_type=None, source_position=None):
        """
        :param is_integer: is an integer data type
        :type is_integer: boolean
        :param is_real: is a real datatype
        :type is_real: boolean
        :param is_string: is a string data type
        :type is_string: boolean
        :param is_boolean: is a boolean
        :type is_boolean: boolean
        :param is_void: is a void data type
        :type is_void: boolean
        :param is_unit_type: an object of type ASTUnitType
        :type is_unit_type: ASTUnitType
        :param source_position: The source position of the assignment
        :type source_position: ASTSourceLocation
        """
        super(ASTDataType, self).__init__(source_position)
        self.__isUnitType = is_unit_type
        self.__isVoid = is_void
        self.__isBoolean = is_boolean
        self.__isString = is_string
        self.__isReal = is_real
        self.__isInteger = is_integer
        return

    def is_integer(self):
        """
        Returns whether this is a integer type or not.
        :return: True if integer typed, otherwise False.
        :rtype: bool
        """
        return isinstance(self.__isInteger, bool) and self.__isInteger

    def is_real(self):
        """
        Returns whether this is a real type or not.
        :return: True if real typed, otherwise False.
        :rtype: bool
        :return: 
        :rtype: 
        """
        return isinstance(self.__isReal, bool) and self.__isReal

    def is_string(self):
        """
        Returns whether this is a string type or not.
        :return: True if string typed, otherwise False.
        :rtype: bool
        """
        return isinstance(self.__isString, bool) and self.__isString

    def is_boolean(self):
        """
        Returns whether this is a boolean type or not.
        :return: True if boolean typed, otherwise False.
        :rtype: bool
        """
        return isinstance(self.__isBoolean, bool) and self.__isBoolean

    def is_void(self):
        """
        Returns whether this is a void type or not.
        :return: True if void typed, otherwise False.
        :rtype: bool
        """
        return isinstance(self.__isVoid, bool) and self.__isVoid

    def is_unit_type(self):
        """
        Returns whether this is a unit type or not.
        :return: True if unit type typed, otherwise False.
        :rtype: bool
        """
        return self.__isUnitType is not None

    def get_unit_type(self):
        """
        Returns the unit type.
        :return: the unit type object.
        :rtype: ASTUnitType
        """
        return self.__isUnitType

    def get_type_symbol(self):
        """
        Returns the corresponding type symbol.
        :return: a single type symbol element.
        :rtype: TypeSymbol
        """
        return self.__typeSymbol

    def set_type_symbol(self, type_symbol):
        """
        Updates the current type symbol to the handed over one.
        :param type_symbol: a new type symbol element.
        :type type_symbol: TypeSymbol.
        """
        from pynestml.symbols.TypeSymbol import TypeSymbol
        assert (type_symbol is not None and isinstance(type_symbol, TypeSymbol)), \
            '(PyNestML.AST.DataType) No or wrong type of type symbol provided (%s)!' % (type(type_symbol))
        self.__typeSymbol = type_symbol
        return

    def get_parent(self, ast):
        """
        Indicates whether a this node contains the handed over node.
        :param ast: an arbitrary meta_model node.
        :type ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        if self.is_unit_type():
            if self.get_unit_type() is ast:
                return self
            elif self.get_unit_type().get_parent(ast) is not None:
                return self.get_unit_type().get_parent(ast)
        return None

    def __str__(self):
        """
        Returns a string representation of the data type.
        :return: a string representation
        :rtype: str
        """
        if self.is_void():
            return 'void'
        elif self.is_string():
            return 'string'
        elif self.is_boolean():
            return 'boolean'
        elif self.is_integer():
            return 'integer'
        elif self.is_real():
            return 'real'
        elif self.is_unit_type():
            return str(self.get_unit_type())
        else:
            raise RuntimeError('Type of datatype not specified!')

    def equals(self, other):
        """
        The equals method.
        :param other: a different object
        :type other: object
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if not isinstance(other, ASTDataType):
            return False
        if not (self.is_integer() == other.is_integer() and self.is_real() == other.is_real() and
                self.is_string() == other.is_string() and self.is_boolean() == other.is_boolean() and
                self.is_void() == other.is_void()):
            return False
        # only one of them uses a unit, thus false
        if self.is_unit_type() + other.is_unit_type() == 1:
            return False
        if self.is_unit_type() and other.is_unit_type() and not self.get_unit_type().equals(other.get_unit_type()):
            return False
        return True
