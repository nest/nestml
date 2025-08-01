# -*- coding: utf-8 -*-
#
# ode_toolbox_expression_printer.py
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

from pynestml.codegeneration.printers.cpp_expression_printer import CppExpressionPrinter
from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_expression_node import ASTExpressionNode
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression


class ODEToolboxExpressionPrinter(CppExpressionPrinter):
    r"""
    Printer for ``ASTExpression`` nodes in ODE-toolbox (sympy) syntax.
    """

    def _print_ternary_operator_expression(self, node: ASTExpression) -> str:
        """
        Prints a ternary operator using the sympy.Piecewise class.
        :return: a string representation
        """
        condition = self.print(node.get_condition())
        if_true = self.print(node.get_if_true())
        if_not = self.print(node.if_not)

        return "Piecewise((" + if_true + ", " + condition + "), (" + if_not + ", True))"

    def _print_arithmetic_operator_expression(self, node: ASTExpressionNode) -> str:
        """
        Prints an arithmetic operator.
        :param op: an arithmetic operator object
        :return: a string representation
        """
        op = node.get_binary_operator()
        lhs = self.print(node.get_lhs())
        rhs = self.print(node.get_rhs())

        if op.is_pow_op:
            # Check if the SimpleExpression has a variable which is the same as its unit type.
            # For example, if an expression is of the form ``x pA = 0 pA**-1``, simple expression on the lhs is ``0pA``, and the rhs is ``-1``.
            # This simple expression will have 0 stored as a numeric literal and ``pA`` as a variable.
            # In this case, the printer must only print the lhs, which is the numeric literal, as the rhs is the exponent of the unit pA.
            if isinstance(node.get_lhs(), ASTSimpleExpression) and node.get_lhs().get_variable() is not None \
                    and node.get_lhs().get_variable().get_name() == node.get_lhs().type.get_symbol_name():
                return lhs
            return lhs + "**" + rhs

        if op.is_plus_op:
            return lhs + " + " + rhs

        if op.is_minus_op:
            return lhs + " - " + rhs

        if op.is_times_op:
            return lhs + " * " + rhs

        if op.is_div_op:
            return lhs + " / " + rhs

        if op.is_modulo_op:
            return "sympy.Mod(" + lhs + ", " + rhs + ")"

        raise RuntimeError("Cannot determine arithmetic operator!")
