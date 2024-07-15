# -*- coding: utf-8 -*-
#
# ast_unit_type.py
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

from typing import List

from pynestml.meta_model.ast_node import ASTNode
from pynestml.utils.cloning_helpers import clone_numeric_literal


class ASTUnitType(ASTNode):
    """
    This class stores information regarding unit types and their properties.
    ASTUnitType. Represents an unit datatype. It can be a plain datatype as 'mV' or a
    complex data type as 'mV/s'

    unitType : leftParentheses='(' unitType rightParentheses=')'
               | base=unitType powOp='**' exponent=UNSIGNED_INTEGER
               | left=unitType (timesOp='*' | divOp='/') right=unitType
               | unitlessLiteral=UNSIGNED_INTEGER divOp='/' right=unitType
               | unit=NAME;
    Attributes:
        # encapsulated or not
        is_encapsulated = False
        compound_unit = None
        # pow rhs
        base = None
        is_pow = False
        exponent = None
        # arithmetic combination case
        lhs = None
        is_times = False
        is_div = False
        rhs = None
        # simple case, just a name
        unit = None
        # the corresponding symbol
        type_symbol = None
    """

    def __init__(self, is_encapsulated=False, compound_unit=None, base=None, is_pow=False,
                 exponent=None, lhs=None, rhs=None, is_div=False, is_times=False, _unit=None, type_symbol=None, *args, **kwargs):
        """
        Standard constructor.

        Parameters for superclass (ASTNode) can be passed through :python:`*args` and :python:`**kwargs`.

        :param compound_unit: a unit encapsulated in brackets
        :type compound_unit: ASTUnitType
        :param base: the base rhs
        :type base: ASTUnitType
        :param is_pow: is a power rhs
        :type is_pow: bool
        :param exponent: the exponent rhs
        :type exponent: int
        :param lhs: the left-hand side rhs
        :type lhs: ASTUnitType or Integer
        :param rhs: the right-hand side rhs
        :type rhs: ASTUnitType
        :param is_div: is a division rhs
        :type is_div: bool
        :param is_times: is a times rhs
        :type is_times: bool
        :param _unit: is a single unit, e.g. mV
        :type _unit: string
        :param type_symbol: the corresponding type symbol
        :type type_symbol: TypeSymbol
        """
        super(ASTUnitType, self).__init__(*args, **kwargs)
        if _unit:
            assert type(_unit) is str
        self.is_encapsulated = is_encapsulated
        self.compound_unit = compound_unit
        self.base = base
        self.is_pow = is_pow
        self.exponent = exponent
        self.lhs = lhs
        self.is_times = is_times
        self.is_div = is_div
        self.rhs = rhs
        self.unit = _unit
        self.type_symbol = type_symbol

    def clone(self):
        """
        Return a clone ("deep copy") of this node.

        :return: new AST node instance
        :rtype: ASTAssignment
        """
        lhs_dup = None
        if self.lhs:
            if isinstance(self.lhs, ASTNode):
                lhs_dup = self.lhs.clone()
            else:
                lhs_dup = clone_numeric_literal(self.lhs)
        rhs_dup = None
        if self.rhs:
            rhs_dup = self.rhs.clone()
        base_dup = None
        if self.base:
            base_dup = self.base.clone()
        compound_unit_dup = None
        if self.compound_unit:
            compound_unit_dup = self.compound_unit.clone()
        dup = ASTUnitType(is_encapsulated=self.is_encapsulated,
                          compound_unit=compound_unit_dup,
                          base=base_dup,
                          is_pow=self.is_pow,
                          exponent=self.exponent,
                          lhs=lhs_dup,
                          rhs=rhs_dup,
                          is_div=self.is_div,
                          is_times=self.is_times,
                          _unit=self.unit,
                          type_symbol=self.type_symbol,
                          # ASTNode common attributes:
                          source_position=self.source_position,
                          scope=self.scope,
                          comment=self.comment,
                          pre_comments=[s for s in self.pre_comments],
                          in_comment=self.in_comment,
                          implicit_conversion_factor=self.implicit_conversion_factor)

        return dup

    def is_simple_unit(self):
        """
        Returns whether the rhs is a simple unit, e.g., mV.
        :return: True if simple unit, otherwise False.
        :rtype: bool
        """
        return self.unit is not None

    def is_arithmetic_expression(self):
        """
        Returns whether the rhs is a arithmetic combination, e.g, mV/mS.
        :return: True if arithmetic rhs, otherwise false.
        :rtype: bool
        """
        return self.lhs is not None and self.rhs is not None and (self.is_div or self.is_times)

    def get_lhs(self):
        """
        Returns the left-hand side rhs if present.
        :return: ASTUnitType instance if present, otherwise None.
        :rtype: ASTUnitType
        """
        return self.lhs

    def get_rhs(self):
        """
        Returns the right-hand side rhs if present.
        :return: ASTUnitType instance if present, otherwise None.
        :rtype: ASTUnitType
        """
        return self.rhs

    def get_type_symbol(self):
        return self.type_symbol

    def set_type_symbol(self, type_symbol):
        self.type_symbol = type_symbol

    def get_children(self) -> List[ASTNode]:
        r"""
        Returns the children of this node, if any.
        :return: List of children of this node.
        """
        if self.is_encapsulated:
            return [self.compound_unit]

        if self.is_pow:
            return [self.base]

        if self.is_arithmetic_expression():
            children = []
            if self.get_lhs() and isinstance(self.get_lhs(), ASTNode):
                children.append(self.get_lhs())

            if self.get_rhs() and isinstance(self.get_rhs(), ASTNode):
                children.append(self.get_rhs())

            return children

        return []

    def equals(self, other: ASTNode) -> bool:
        r"""
        The equality method.
        """
        if not isinstance(other, ASTUnitType):
            return False
        if self.is_encapsulated + other.is_encapsulated == 1:
            return False
        if self.is_encapsulated and other.is_encapsulated and not self.compound_unit.equals(other.compound_unit):
            return False
        if self.is_pow + other.is_pow == 1:
            return False
        if self.is_pow and other.is_pow and \
                not (self.base.equals(other.base) and self.exponent == other.exponent):
            return False
        if self.is_arithmetic_expression() + other.is_arithmetic_expression() == 1:
            return False
        if self.is_arithmetic_expression() and other.is_arithmetic_expression() and \
                not (self.get_lhs().equals(other.lhs) and self.rhs.equals(other.rhs)
                     and self.is_times == other.is_times and self.is_div == other.is_div):
            return False
        if self.is_simple_unit() + other.is_simple_unit() == 1:
            return False
        if self.is_simple_unit() and other.is_simple_unit() and not self.unit == other.unit:
            return False
        return True
