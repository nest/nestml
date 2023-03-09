# -*- coding: utf-8 -*-
#
# latex_expression_printer.py
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

import re

from pynestml.codegeneration.printers.expression_printer import ExpressionPrinter
from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_expression_node import ASTExpressionNode
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.utils.ast_utils import ASTUtils


class LatexExpressionPrinter(ExpressionPrinter):
    r"""
    Expressions printer for LaTeX. Assumes to be printing in a LaTeX environment where math mode is already on.
    """

    def print(self, node: ASTExpressionNode) -> str:
        if node.get_implicit_conversion_factor() is not None \
           and str(node.get_implicit_conversion_factor()) not in ["1.", "1.0", "1"]:
            return str(node.get_implicit_conversion_factor()) + " * (" + self.print_expression(node) + ")"

        return self.print_expression(node)

    def print_expression(self, node: ASTExpressionNode) -> str:
        if isinstance(node, ASTVariable):
            return self._simple_expression_printer._variable_printer.print_variable(node)

        if isinstance(node, ASTSimpleExpression):
            return self._simple_expression_printer.print(node)

        if isinstance(node, ASTExpression):
            # a unary operator
            if node.is_unary_operator():
                op = self._print_unary_operator(node.get_unary_operator())
                rhs = self.print_expression(node.get_expression())
                return op % rhs

            # encapsulated in brackets
            if node.is_encapsulated:
                return self._print_encapsulated() % self.print_expression(node.get_expression())

            # logical not
            if node.is_logical_not:
                op = self._print_logical_not()
                rhs = self.print_expression(node.get_expression())
                return op % rhs

            # compound rhs with lhs + rhs
            if node.is_compound_expression():
                lhs = self.print_expression(node.get_lhs())
                rhs = self.print_expression(node.get_rhs())
                wide = False
                if node.get_binary_operator().is_div_op \
                        and len(lhs) > 3 * len(rhs):
                    # if lhs (numerator) is much wider than rhs (denominator), rewrite as a factor
                    wide = True
                op = self._print_binary_op(node.get_binary_operator(), wide=wide)
                return op % ({"lhs": lhs, "rhs": rhs})

            if node.is_ternary_operator():
                condition = self.print_expression(node.get_condition())
                if_true = self.print_expression(node.get_if_true())
                if_not = self.print_expression(node.if_not)
                return "(" + condition + ") ? (" + if_true + ") : (" + if_not + ")"

            raise Exception("Unknown node type")

        raise RuntimeError("Tried to print unknown expression: \"%s\"" % str(node))

    def _print_unary_operator(self, ast_unary_operator) -> str:
        """
        Print unary operator.

        :param ast_unary_operator: a unary operator
        :type ast_unary_operator: ASTUnaryOperator
        :return: the corresponding string representation
        """
        return str(ast_unary_operator) + "%s"

    def print_function_call(self, function_call) -> str:
        r"""
        Print function call.

        :param function_call: a function call
        :type function_call: ASTFunctionCall
        :return: the corresponding string representation
        """
        result = function_call.get_name()

        symbols = {
            "convolve": r"\\text{convolve}"
        }

        for symbol_find, symbol_replace in symbols.items():
            result = re.sub(r"(?<![a-zA-Z])(" + symbol_find + ")(?![a-zA-Z])",
                            symbol_replace, result)  # "whole word" match

        if ASTUtils.needs_arguments(function_call):
            n_args = len(function_call.get_args())
            result += "(" + ", ".join(["%s" for _ in range(n_args)]) + ")"
        else:
            result += "()"

        return result

    def _print_binary_op(self, ast_binary_operator, wide=False) -> str:
        """
        Print binary operator.

        :param ast_binary_operator: a single binary operator
        :type ast_binary_operator: ASTBinaryOperator
        :return: the corresponding string representation
        """
        if ast_binary_operator.is_div_op:
            if wide:
                return r"\frac 1 { %(rhs)s } \left( { %(lhs)s } \right) "

            return r"\frac{ %(lhs)s } { %(rhs)s }"

        if ast_binary_operator.is_times_op:
            return r"%(lhs)s \cdot %(rhs)s"

        if ast_binary_operator.is_pow_op:
            return r"{ %(lhs)s }^{ %(rhs)s }"

        return r"%(lhs)s" + str(ast_binary_operator) + r"%(rhs)s"

    def _print_encapsulated(self) -> str:
        return r"(%s)"

    def _print_logical_not(self) -> str:
        return r"\neg%s"
