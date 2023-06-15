# -*- coding: utf-8 -*-
#
# ast_variable.py
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

from typing import Any, Optional

from copy import copy

from pynestml.meta_model.ast_node import ASTNode
from pynestml.symbols.type_symbol import TypeSymbol


class ASTVariable(ASTNode):
    r"""
    This class is used to store a single variable.

    ASTVariable Provides a 'marker' AST node to identify variables used in expressions.
    Grammar:
        variable : NAME (differentialOrder='\'')*;
    Attributes:
        name = None
        differential_order = None
        # the corresponding type symbol
        type_symbol = None
    """

    def __init__(self, name, differential_order=0, type_symbol: Optional[str] = None,
                 vector_parameter: Optional[str] = None, is_homogeneous: bool = False, delay_parameter: Optional[str] = None, *args, **kwargs):
        """
        Standard constructor.
        :param name: the name of the variable
        :type name: str
        :param differential_order: the differential order of the variable.
        :type differential_order: int
        :param type_symbol: the type of the variable
        :param vector_parameter: the vector parameter of the variable
        :param delay_parameter: the delay value to be used in the differential equation
        """
        super(ASTVariable, self).__init__(*args, **kwargs)
        assert isinstance(differential_order, int), \
            '(PyNestML.AST.Variable) No or wrong type of differential order provided (%s)!' % type(differential_order)
        assert (differential_order >= 0), \
            '(PyNestML.AST.Variable) Differential order must be at least 0, is %d!' % differential_order
        assert isinstance(name, str), \
            '(PyNestML.AST.Variable) No or wrong type of name provided (%s)!' % type(name)
        self.name = name
        self.differential_order = differential_order
        self.type_symbol = type_symbol
        self.vector_parameter = vector_parameter
        self.is_homogeneous = is_homogeneous
        self.delay_parameter = delay_parameter

    def clone(self):
        r"""
        Return a clone ("deep copy") of this node.
        """
        return ASTVariable(name=self.name,
                           differential_order=self.differential_order,
                           type_symbol=self.type_symbol,
                           vector_parameter=self.vector_parameter,
                           delay_parameter=self.delay_parameter,
                           # ASTNode common attriutes:
                           source_position=self.get_source_position(),
                           scope=self.scope,
                           comment=self.comment,
                           pre_comments=[s for s in self.pre_comments],
                           in_comment=self.in_comment,
                           implicit_conversion_factor=self.implicit_conversion_factor)

    def resolve_in_own_scope(self):
        from pynestml.symbols.symbol import SymbolKind
        assert self.get_scope() is not None
        return self.get_scope().resolve_to_symbol(self.get_complete_name(), SymbolKind.VARIABLE)

    def get_name(self) -> str:
        r"""
        Returns the name of the variable.
        :return: the name of the variable.
        """
        return self.name

    def set_name(self, name: str) -> None:
        """
        Sets the name of the variable.
        :name: the name to set.
        """
        self.name = name

    def get_is_homogeneous(self) -> bool:
        return self.is_homogeneous

    def get_differential_order(self) -> int:
        r"""
        Returns the differential order of the variable.
        :return: the differential order.
        """
        return self.differential_order

    def set_differential_order(self, differential_order: int) -> None:
        r"""
        Returns the differential order of the variable.
        """
        self.differential_order = differential_order

    def get_complete_name(self) -> str:
        r"""
        Returns the complete name, consisting of the name and the differential order.
        :return: the complete name.
        """
        return self.get_name() + '\'' * self.get_differential_order()

    def get_name_of_lhs(self) -> str:
        r"""
        Returns the complete name but with differential order reduced by one.
        :return: the name.
        """
        if self.get_differential_order() > 0:
            return self.get_name() + '\'' * (self.get_differential_order() - 1)
        return self.get_name()

    def get_type_symbol(self) -> TypeSymbol:
        r"""
        Returns the type symbol of this rhs.
        :return: a single type symbol.
        """
        return copy(self.type_symbol)

    def set_type_symbol(self, type_symbol: TypeSymbol):
        r"""
        Updates the current type symbol to the handed over one.
        :param type_symbol: a single type symbol object.
        """
        self.type_symbol = type_symbol

    def has_vector_parameter(self) -> bool:
        r"""
        Returns the vector parameter of the variable
        :return: the vector parameter
        """
        return self.vector_parameter is not None

    def get_vector_parameter(self) -> str:
        r"""
        Returns the vector parameter of the variable
        :return: the vector parameter
        """
        return self.vector_parameter

    def set_vector_parameter(self, vector_parameter):
        r"""
        Updates the vector parameter of the variable
        """
        self.vector_parameter = vector_parameter

    def get_delay_parameter(self):
        r"""
        Returns the delay parameter
        :return: delay parameter
        """
        return self.delay_parameter

    def set_delay_parameter(self, delay: str):
        """
        Updates the current delay parameter to the handed over value
        :param delay: delay parameter
        """
        assert (delay is not None), '(PyNestML.AST.Variable) No delay parameter provided'
        self.delay_parameter = delay

    def get_parent(self, ast: ASTNode) -> Optional[ASTNode]:
        """
        Indicates whether a this node contains the handed over node.
        :param ast: an arbitrary meta_model node.
        :return: AST if this or one of the child nodes contains the handed over element.
        """
        return None

    def is_unit_variable(self) -> bool:
        r"""
        Provided on-the-fly information whether this variable represents a unit-variable, e.g., nS.
        Caution: It assumes that the symbol table has already been constructed.
        :return: True if unit-variable, otherwise False.
        """
        from pynestml.symbols.predefined_types import PredefinedTypes
        if self.get_name() in PredefinedTypes.get_types():
            return True
        return False

    def equals(self, other: Any) -> bool:
        r"""
        The equals method.
        :param other: a different object.
        :return: True if equals, otherwise False.
        """
        if not isinstance(other, ASTVariable):
            return False
        return self.get_name() == other.get_name() and self.get_differential_order() == other.get_differential_order()

    def is_delay_variable(self) -> bool:
        """
        Returns whether it is a delay variable or not
        :return: True if the variable has a delay parameter, False otherwise
        """
        return self.get_delay_parameter() is not None
