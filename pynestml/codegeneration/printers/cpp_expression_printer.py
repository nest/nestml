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

from pynestml.codegeneration.printers.expression_printer import ExpressionPrinter
from pynestml.meta_model.ast_arithmetic_operator import ASTArithmeticOperator
from pynestml.meta_model.ast_bit_operator import ASTBitOperator
from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_expression_node import ASTExpressionNode
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.meta_model.ast_logical_operator import ASTLogicalOperator
from pynestml.meta_model.ast_comparison_operator import ASTComparisonOperator
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_node_factory import ASTNodeFactory
from pynestml.utils.ast_source_location import ASTSourceLocation


class CppExpressionPrinter(ExpressionPrinter):
    r"""
    Printer for ``ASTExpression`` nodes in C++ syntax.
    """

    def print(self, node: ASTNode) -> str:
        if isinstance(node, ASTExpression):
            if node.get_implicit_conversion_factor() and not node.get_implicit_conversion_factor() == 1:
                return "(" + str(node.get_implicit_conversion_factor()) + " * (" + self.print_expression(node) + "))"

            return self.print_expression(node)

        return self._simple_expression_printer.print(node)

    def print_expression(self, node: ASTExpressionNode) -> str:
        assert isinstance(node, ASTExpression)

        if node.is_unary_operator():
            return self._print_unary_op_expression(node)

        if node.is_encapsulated:
            return self._print_encapsulated_expression(node)

        if node.is_logical_not:
            return self._print_logical_not_expression(node)

        if node.is_compound_expression():
            return self._print_binary_op_expression(node)

        if node.is_ternary_operator():
            return self._print_ternary_operator_expression(node)

        if node.is_expression():
            return self.print_expression(node.get_expression())

        raise RuntimeError("Tried to print unknown expression: \"%s\"" % str(node))

    def _print_unary_op_expression(self, node: ASTExpressionNode) -> str:
        """
        Prints a unary operator.
        :param node: an expression with unary operator
        :return: a string representation
        """
        rhs = self.print(node.get_expression())
        unary_operator = node.get_unary_operator()
        if unary_operator.is_unary_plus:
            return "(" + "+" + rhs + ")"

        if unary_operator.is_unary_minus:
            return "(" + "-" + rhs + ")"

        if unary_operator.is_unary_tilde:
            return "(" + "~" + rhs + ")"

        raise RuntimeError("Cannot determine unary operator!")

    def _print_encapsulated_expression(self, node: ASTExpression) -> str:
        """
        Prints the encapsulating parenthesis of an expression.
        :return: a string representation
        """
        expr = self.print(node.get_expression())

        return "(" + expr + ")"

    def _print_logical_not_expression(self, node: ASTExpression) -> str:
        """
        Prints a logical NOT operator.
        :return: a string representation
        """
        rhs = self.print(node.get_expression())

        return "(" + "!" + rhs + ")"

    def _print_logical_operator_expression(self, node: ASTExpressionNode) -> str:
        """
        Prints a logical operator.
        :param node: an expression with logical operator
        :return: a string representation
        """
        op = node.get_binary_operator()
        lhs = self.print(node.get_lhs())
        rhs = self.print(node.get_rhs())

        if op.is_logical_and:
            return lhs + " && " + rhs

        if op.is_logical_or:
            return lhs + " || " + rhs

        raise RuntimeError("Cannot determine logical operator!")

    def _print_comparison_operator_expression(self, node: ASTExpressionNode) -> str:
        """
        Prints a comparison operator.
        :param node: an expression with comparison operator
        :return: a string representation
        """
        op = node.get_binary_operator()
        lhs = self.print(node.get_lhs())
        rhs = self.print(node.get_rhs())

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

    def _print_bit_operator_expression(self, node: ASTExpressionNode) -> str:
        """
        Prints a bit operator in NEST syntax.
        :param node: an expression with a bit operator
        :return: a string representation
        """
        op = node.get_binary_operator()
        lhs = self.print(node.get_lhs())
        rhs = self.print(node.get_rhs())

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

    def _print_arithmetic_operator_expression(self, node: ASTExpressionNode) -> str:
        """
        Prints an arithmetic operator.
        :param node: an expression with arithmetic operator
        :return: a string representation
        """
        op = node.get_binary_operator()

        if op.is_pow_op:
            # make a dummy ASTFunctionCall so we can delegate this to the FunctionCallPrinter
            dummy_ast_function_call: ASTFunctionCall = ASTNodeFactory.create_ast_function_call(callee_name="pow", args=(node.get_lhs(), node.get_rhs()), source_position=ASTSourceLocation.get_added_source_position())
            return self._simple_expression_printer._function_call_printer.print(dummy_ast_function_call)

        lhs = self.print(node.get_lhs())
        rhs = self.print(node.get_rhs())

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

        raise RuntimeError("Cannot determine arithmetic operator!")

    def _print_ternary_operator_expression(self, node: ASTExpression) -> str:
        """
        Prints a ternary operator.
        :return: a string representation
        """
        condition = self.print(node.get_condition())
        if_true = self.print(node.get_if_true())
        if_not = self.print(node.if_not)

        return "(" + condition + ") ? (" + if_true + ") : (" + if_not + ")"

    def _print_binary_op_expression(self, node: ASTExpressionNode) -> str:
        """
        Prints a binary operator.
        :param node: an expression with binary operator
        :return: a string representation
        """

        binary_operator = node.get_binary_operator()

        if isinstance(binary_operator, ASTArithmeticOperator):
            return self._print_arithmetic_operator_expression(node)

        if isinstance(binary_operator, ASTBitOperator):
            return self._print_bit_operator_expression(node)

        if isinstance(binary_operator, ASTComparisonOperator):
            return self._print_comparison_operator_expression(node)

        if isinstance(binary_operator, ASTLogicalOperator):
            return self._print_logical_operator_expression(node)

        raise RuntimeError("Cannot determine binary operator!")
