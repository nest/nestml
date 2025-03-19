# -*- coding: utf-8 -*-
#
# nestml_expression_printer.py
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

from pynestml.codegeneration.printers.expression_printer import ExpressionPrinter
from pynestml.meta_model.ast_arithmetic_operator import ASTArithmeticOperator
from pynestml.meta_model.ast_comparison_operator import ASTComparisonOperator
from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_logical_operator import ASTLogicalOperator
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.meta_model.ast_unary_operator import ASTUnaryOperator


class NESTMLExpressionPrinter(ExpressionPrinter):
    r"""
    Printer for ``ASTExpression`` nodes in NESTML syntax.
    """

    def print(self, node: ASTNode) -> str:
        if isinstance(node, ASTExpression):
            if node.get_implicit_conversion_factor() and not node.get_implicit_conversion_factor() == 1:
                return "(" + str(node.get_implicit_conversion_factor()) + " * (" + self.print_expression(node) + "))"

            return self.print_expression(node)

        if isinstance(node, ASTArithmeticOperator):
            return self.print_arithmetic_operator(node)

        if isinstance(node, ASTUnaryOperator):
            return self.print_unary_operator(node)

        if isinstance(node, ASTComparisonOperator):
            return self.print_comparison_operator(node)

        if isinstance(node, ASTLogicalOperator):
            return self.print_logical_operator(node)

        return self._simple_expression_printer.print(node)

    def print_logical_operator(self, node: ASTLogicalOperator) -> str:
        if node.is_logical_and:
            return " and "

        if node.is_logical_or:
            return " or "

        raise Exception("Unknown logical operator")

    def print_comparison_operator(self, node: ASTComparisonOperator) -> str:
        if node.is_lt:
            return " < "

        if node.is_le:
            return " <= "

        if node.is_eq:
            return " == "

        if node.is_ne:
            return " != "

        if node.is_ne2:
            return " <> "

        if node.is_ge:
            return " >= "

        if node.is_gt:
            return " > "

        raise RuntimeError("Type of comparison operator not specified!")

    def print_unary_operator(self, node: ASTUnaryOperator) -> str:
        if node.is_unary_plus:
            return "+"

        if node.is_unary_minus:
            return "-"

        if node.is_unary_tilde:
            return "~"

        raise RuntimeError("Type of unary operator not specified!")

    def print_arithmetic_operator(self, node: ASTArithmeticOperator) -> str:
        if node.is_times_op:
            return " * "

        if node.is_div_op:
            return " / "

        if node.is_modulo_op:
            return " % "

        if node.is_plus_op:
            return " + "

        if node.is_minus_op:
            return " - "

        if node.is_pow_op:
            return " ** "

        raise RuntimeError("Arithmetic operator not specified.")

    def print_expression(self, node: ASTExpression) -> str:
        ret = ""
        if node.is_expression():
            if node.is_encapsulated:
                ret += "("

            if node.is_logical_not:
                ret += "not "

            if node.is_unary_operator():
                ret += self.print_unary_operator(node.get_unary_operator())

            if isinstance(node.get_expression(), ASTExpression):
                ret += self.print_expression(node.get_expression())
            elif isinstance(node.get_expression(), ASTSimpleExpression):
                ret += self._simple_expression_printer.print_simple_expression(node.get_expression())
            else:
                raise RuntimeError("Unknown node type")

            if node.is_encapsulated:
                ret += ")"

        elif node.is_compound_expression():
            if isinstance(node.get_lhs(), ASTExpression):
                ret += self.print_expression(node.get_lhs())
            elif isinstance(node.get_lhs(), ASTSimpleExpression):
                ret += self._simple_expression_printer.print_simple_expression(node.get_lhs())
            else:
                raise RuntimeError("Unknown node type")

            ret += self.print(node.get_binary_operator())

            if isinstance(node.get_rhs(), ASTExpression):
                ret += self.print_expression(node.get_rhs())
            elif isinstance(node.get_rhs(), ASTSimpleExpression):
                ret += self._simple_expression_printer.print_simple_expression(node.get_rhs())
            else:
                raise RuntimeError("Unknown node type")

        elif node.is_ternary_operator():
            ret += self.print(node.get_condition()) + "?" + self.print(
                node.get_if_true()) + ":" + self.print(node.get_if_not())

        return ret
