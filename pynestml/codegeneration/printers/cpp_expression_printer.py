# -*- coding: utf-8 -*-
#
# cpp_expression_printer.py
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

from typing import Optional, Tuple, Union

from pynestml.codegeneration.printers.ast_printer import ASTPrinter
from pynestml.codegeneration.printers.cpp_simple_expression_printer import CppSimpleExpressionPrinter
from pynestml.codegeneration.printers.expression_printer import ExpressionPrinter
from pynestml.meta_model.ast_arithmetic_operator import ASTArithmeticOperator
from pynestml.meta_model.ast_bit_operator import ASTBitOperator
from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_expression_node import ASTExpressionNode
from pynestml.meta_model.ast_logical_operator import ASTLogicalOperator
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.meta_model.ast_comparison_operator import ASTComparisonOperator
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_unary_operator import ASTUnaryOperator
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression


class CppExpressionPrinter(ExpressionPrinter):
    r"""
    Printer for ``ASTExpression`` nodes in C++ syntax.
    """

    def print(self, node: ASTNode, prefix: str = "") -> str:
        if isinstance(node, ASTExpression):
            return self._print(node, prefix)

        return self._simple_expression_printer.print(node, prefix)

    def _print(self, node: ASTNode, prefix: str = "") -> str:
        assert isinstance(node, ASTExpression)

        if node.get_implicit_conversion_factor() and not node.get_implicit_conversion_factor() == 1:
            return "(" + str(node.get_implicit_conversion_factor()) + " * (" + self.print_expression(node, prefix=prefix) + "))"

        return self.print_expression(node, prefix=prefix)

    def print_expression(self, node: ASTExpressionNode, prefix: str = "") -> str:
        assert isinstance(node, ASTExpression)
        if node.is_unary_operator():
            return self.print_unary_op(node, prefix=prefix)

        if node.is_encapsulated:
            return self.print_encapsulated(node, prefix=prefix)

        if node.is_logical_not:
            return self.print_logical_not(node, prefix=prefix)

        if node.is_compound_expression():
            return self.print_binary_op(node, prefix=prefix)

        if node.is_ternary_operator():
            return self.print_ternary_operator(node, prefix=prefix)

        raise RuntimeError("Tried to print unknown expression: \"%s\"" % str(node))

    def print_unary_op(self, node: ASTExpressionNode, prefix: str = "") -> str:
        """
        Prints a unary operator.
        :param unary_operator: an operator object
        :return: a string representation
        """
        rhs = self.print(node.get_expression(), prefix=prefix)
        unary_operator = node.get_unary_operator()
        if unary_operator.is_unary_plus:
            return "(" + "+" + rhs + ")"

        if unary_operator.is_unary_minus:
            return "(" + "-" + rhs + ")"

        if unary_operator.is_unary_tilde:
            return "(" + "~" + rhs + ")"

        raise RuntimeError("Cannot determine unary operator!")

    def print_encapsulated(self, node: ASTExpression, prefix: str = "") -> str:
        """
        Prints the encapsulating parenthesis of an expression.
        :return: a string representation
        """
        expr = self.print(node.get_expression(),
                          prefix=prefix)

        return "(" + expr + ")"

    def print_logical_not(self, node: ASTExpression, prefix: str = "") -> str:
        """
        Prints a logical NOT operator.
        :return: a string representation
        """
        rhs = self.print(node.get_expression(), prefix=prefix)

        return "(" + "!" + "%s" + ")" % rhs

    def print_logical_operator(self, node: ASTExpressionNode, prefix: str = "") -> str:
        """
        Prints a logical operator.
        :param op: a logical operator object
        :return: a string representation
        """
        op = node.get_binary_operator()
        lhs = self.print(node.get_lhs(), prefix=prefix)
        rhs = self.print(node.get_rhs(), prefix=prefix)

        if op.is_logical_and:
            return lhs + "&&" + rhs

        if op.is_logical_or:
            return lhs + "||" + rhs

        raise RuntimeError("Cannot determine logical operator!")

    def print_comparison_operator(self, node: ASTExpressionNode, prefix: str = "") -> str:
        """
        Prints a comparison operator.
        :param op: a comparison operator object
        :return: a string representation
        """
        op = node.get_binary_operator()
        lhs = self.print(node.get_lhs(), prefix=prefix)
        rhs = self.print(node.get_rhs(), prefix=prefix)

        if op.is_lt:
            return lhs + " < " + rhs

        if op.is_le:
            return lhs + " <= " + rhs

        if op.is_eq:
            return lhs + " == " + rhs

        if op.is_ne or op.is_ne2:
            return lhs + " != " + rhs

        if op.is_ge:
            return lhs + " >= " + rhs

        if op.is_gt:
            return lhs + " > " + rhs

        raise RuntimeError("Cannot determine comparison operator!")

    def print_bit_operator(self, node: ASTExpressionNode, prefix: str = "") -> str:
        """
        Prints a bit operator in NEST syntax.
        :param op: a bit operator object
        :return: a string representation
        """
        op = node.get_binary_operator()
        lhs = self.print(node.get_lhs(), prefix=prefix)
        rhs = self.print(node.get_rhs(), prefix=prefix)

        if op.is_bit_shift_left:
            return lhs + " << " + rhs

        if op.is_bit_shift_right:
            return lhs + " >> " + rhs

        if op.is_bit_and:
            return lhs + " & " + rhs

        if op.is_bit_or:
            return lhs + " | " + rhs

        if op.is_bit_xor:
            return lhs + " ^ " + rhs

        raise RuntimeError("Cannot determine bit operator!")

    def print_arithmetic_operator(self, node: ASTExpressionNode, prefix: str = "") -> str:
        """
        Prints an arithmetic operator.
        :param op: an arithmetic operator object
        :return: a string representation
        """
        op = node.get_binary_operator()
        lhs = self.print(node.get_lhs(), prefix=prefix)
        rhs = self.print(node.get_rhs(), prefix=prefix)

        if op.is_plus_op:
            return lhs + " + " + rhs

        if op.is_minus_op:
            return lhs + " - " + rhs

        if op.is_times_op:
            return lhs + " * " + rhs

        if op.is_div_op:
            return lhs + " / " + rhs

        if op.is_modulo_op:
            return lhs + " % " + rhs

        if op.is_pow_op:
            return "pow" + "(" + lhs + ", " + rhs + ")"

        raise RuntimeError("Cannot determine arithmetic operator!")

    def print_ternary_operator(self, node: ASTExpression, prefix: str = "") -> str:
        """
        Prints a ternary operator.
        :return: a string representation
        """
        condition = self.print(node.get_condition(), prefix=prefix)
        if_true = self.print(node.get_if_true(), prefix=prefix)
        if_not = self.print(node.if_not, prefix=prefix)

        return "(" + condition + ") ? (" + if_true + ") : (" + if_not + ")"

    def print_binary_op(self, node: ASTExpressionNode, prefix: str = "") -> str:
        """
        Prints a binary operator.
        :param binary_operator: a binary operator object
        :return: a string representation
        """

        binary_operator = node.get_binary_operator()

        if isinstance(binary_operator, ASTArithmeticOperator):
            return self.print_arithmetic_operator(node, prefix)

        if isinstance(binary_operator, ASTBitOperator):
            return self.print_bit_operator(node, prefix)

        if isinstance(binary_operator, ASTComparisonOperator):
            return self.print_comparison_operator(node, prefix)

        if isinstance(binary_operator, ASTLogicalOperator):
            return self.print_logical_operator(node, prefix)

        raise RuntimeError("Cannot determine binary operator!")
