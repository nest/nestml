# -*- coding: utf-8 -*-
#
# ast_dot_operator_visitor.py
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

"""
rhs : left=rhs (timesOp="*" | divOp=("/" | "//") | moduloOp="%") right=rhs
"""
from pynestml.symbols.error_type_symbol import ErrorTypeSymbol
from pynestml.symbols.predefined_types import PredefinedTypes
from pynestml.symbols.type_symbol import TypeSymbol
from pynestml.symbols.unit_type_symbol import UnitTypeSymbol
from pynestml.visitors.ast_visitor import ASTVisitor


class ASTDotOperatorVisitor(ASTVisitor):
    """
    This visitor is used to derive the correct type of expressions which use a binary dot operator.
    """

    def visit_expression(self, node):
        """
        Visits a single rhs and updates the type.
        :param node: a single rhs
        :type node: ast_expression
        """
        lhs_type = node.get_lhs().type
        rhs_type = node.get_rhs().type
        arith_op = node.get_binary_operator()

        lhs_type.referenced_object = node.get_lhs()
        rhs_type.referenced_object = node.get_rhs()

        if arith_op.is_modulo_op:
            node.type = lhs_type % rhs_type
            return
        if arith_op.is_div_op:
            node.type = lhs_type / rhs_type
            return
        if arith_op.is_integer_div_op:
            node.type = self.integer_division_type(lhs_type, rhs_type)
            return
        if arith_op.is_times_op:
            node.type = lhs_type * rhs_type
            return

    @staticmethod
    def integer_division_type(lhs_type: TypeSymbol, rhs_type: TypeSymbol) -> TypeSymbol:
        r"""
        Return the type of the integer division ``lhs // rhs``.

        Integer division truncates the quotient ``lhs / rhs`` to an integer. This is only well-defined if the quotient is dimensionless: the truncation of a physical value depends on the unit in which it is expressed, which differs between target platforms (for instance, 0.5 V truncates to 0 V, but the same voltage, 500 mV, truncates to 500 mV). If the quotient is dimensionless, the result is of type ``integer``. If it is not, the (physical) type of the quotient is returned; the coco CoCoTruncationOperandsDimensionless then reports the error.
        """
        quotient_type = lhs_type / rhs_type
        if isinstance(quotient_type, (ErrorTypeSymbol, UnitTypeSymbol)) or not quotient_type.is_numeric():
            return quotient_type

        return PredefinedTypes.get_integer_type()
