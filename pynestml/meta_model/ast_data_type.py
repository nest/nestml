# -*- coding: utf-8 -*-
#
# ast_data_type.py
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

from typing import Optional

from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_unit_type import ASTUnitType


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
    Attributes:
        is_integer = False
        is_real = False
        is_string = False
        is_boolean = False
        is_void = False
        unit_type = None  # a unit type is not a boolean, but a concrete object
        type_symbol = None  # the corresponding type symbol
    """

    def __init__(self, is_integer=False, is_real=False, is_string=False, is_boolean=False, is_void=False,
                 unit_type: Optional[ASTUnitType] = None, type_symbol=None, *args, **kwargs):
        """
        Standard constructor.

        Parameters for superclass (ASTNode) can be passed through :python:`*args` and :python:`**kwargs`.

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
        :param unit_type: an object of type ASTUnitType
        :type unit_type: ASTUnitType
        """
        super(ASTDataType, self).__init__(*args, **kwargs)
        self.is_integer = is_integer
        self.is_real = is_real
        self.is_string = is_string
        self.is_boolean = is_boolean
        self.is_void = is_void
        self.unit_type = unit_type
        self.type_symbol = type_symbol

    def clone(self):
        """
        Return a clone ("deep copy") of this node.

        :return: new AST node instance
        :rtype: ASTDataType
        """
        unit_type_dup = None
        if self.unit_type:
            unit_type_dup = self.unit_type.clone()
        dup = ASTDataType(is_integer=self.is_integer,
                          is_real=self.is_real,
                          is_string=self.is_string,
                          is_boolean=self.is_boolean,
                          is_void=self.is_void,
                          unit_type=unit_type_dup,
                          type_symbol=self.type_symbol,
                          # ASTNode common attributes:
                          source_position=self.source_position,
                          scope=self.scope,
                          comment=self.comment,
                          pre_comments=[s for s in self.pre_comments],
                          in_comment=self.in_comment,
                          post_comments=[s for s in self.post_comments],
                          implicit_conversion_factor=self.implicit_conversion_factor)

        return dup

    def is_unit_type(self):
        """
        Returns whether this is a unit type or not.
        :return: True if unit type typed, otherwise False.
        :rtype: bool
        """
        return self.unit_type is not None

    def get_unit_type(self):
        """
        Returns the unit type.
        :return: the unit type object.
        :rtype: ASTUnitType
        """
        return self.unit_type

    def get_type_symbol(self):
        """
        Returns the corresponding type symbol.
        :return: a single type symbol element.
        :rtype: type_symbol
        """
        if self.is_unit_type():
            return self.get_unit_type().get_type_symbol()
        return self.type_symbol

    def set_type_symbol(self, type_symbol):
        """
        Updates the current type symbol to the handed over one.
        :param type_symbol: a new type symbol element.
        :type type_symbol: TypeSymbol.
        """
        from pynestml.symbols.type_symbol import TypeSymbol
        assert (type_symbol is not None and isinstance(type_symbol, TypeSymbol)), \
            '(PyNestML.AST.DataType) No or wrong type of type symbol provided (%s)!' % (type(type_symbol))
        self.type_symbol = type_symbol

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
            if self.get_unit_type().get_parent(ast) is not None:
                return self.get_unit_type().get_parent(ast)
        return None

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
        if not (self.is_integer == other.is_integer and self.is_real == other.is_real
                and self.is_string == other.is_string and self.is_boolean == other.is_boolean
                and self.is_void == other.is_void):
            return False
        # only one of them uses a unit, thus false
        if self.is_unit_type() + other.is_unit_type() == 1:
            return False
        if self.is_unit_type() and other.is_unit_type() and not self.get_unit_type().equals(other.get_unit_type()):
            return False
        return True
