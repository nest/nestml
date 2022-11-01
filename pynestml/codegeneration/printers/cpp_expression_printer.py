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

        if isinstance(node, ASTSimpleExpression):
            return self._simple_expression_printer.print(node, prefix)

        if isinstance(node, ASTFunctionCall):
            return self._simple_expression_printer.print_function_call(node)

        raise RuntimeError("Tried to print unknown expression: \"%s\"" % str(node))

    def _print(self, node: ASTExpressionNode, prefix: str = "") -> str:
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

    def print_expression(self, node: ASTExpressionNode, prefix: str = ""):
        r"""Print an expression.

        Parameters
        ----------
        node : ASTExpressionNode
            The expression node to print.
        prefix : str
            *See documentation for the function print_function_call().*

        Returns
        -------
        s : str
            The expression string.
        """
        if (node.get_implicit_conversion_factor() is not None) \
                and (not node.get_implicit_conversion_factor() == 1):
            return str(node.get_implicit_conversion_factor()) + " * (" + self.__print(node, prefix=prefix) + ")"

        return self._print(node, prefix=prefix)

    def print_unary_op(self, unary_operator: ASTUnaryOperator, prefix: str = "") -> str:
        """
        Converts a unary operator.
        :param unary_operator: an operator object
        :return: a string representation
        """
        rhs = self.print_expression(unary_operator.get_expression(), prefix=prefix)

        if unary_operator.is_unary_plus:
            return '(' + '+' + rhs + ')'

        if unary_operator.is_unary_minus:
            return '(' + '-' + rhs + ')'

        if unary_operator.is_unary_tilde:
            return '(' + '~' + rhs + ')'

        raise RuntimeError('Cannot determine unary operator!')

    def print_encapsulated(self, node: ASTExpression, prefix: str = "") -> str:
        """
        Converts the encapsulating parenthesis of an expression.
        :return: a string representation
        """
        expr = self.print_expression(node.get_expression(),
                                     prefix=prefix)

        return '(' + expr + ')'

    def print_logical_not(self, node: ASTExpression, prefix: str = "") -> str:
        """
        Converts a logical NOT operator.
        :return: a string representation
        """
        rhs = self.print_expression(node.get_expression(), prefix=prefix)

        return '(' + '!' + '%s' + ')' % rhs

    def print_logical_operator(self, op: ASTLogicalOperator, prefix: str = "") -> str:
        """
        Converts a logical operator.
        :param op: a logical operator object
        :return: a string representation
        """
        lhs = self.print_expression(op.get_lhs(), prefix=prefix)
        rhs = self.print_expression(op.get_rhs(), prefix=prefix)

        if op.is_logical_and:
            return lhs + '&&' + rhs

        if op.is_logical_or:
            return lhs + '||' + rhs

        raise RuntimeError('Cannot determine logical operator!')

    def print_comparison_operator(self, op: ASTComparisonOperator, prefix: str = "")-> str:
        """
        Converts a comparison operator.
        :param op: a comparison operator object
        :return: a string representation
        """
        lhs = self.print_expression(op.get_lhs(), prefix=prefix)
        rhs = self.print_expression(op.get_rhs(), prefix=prefix)

        if op.is_lt:
            return lhs +'<' + rhs

        if op.is_le:
            return lhs +'<=' + rhs

        if op.is_eq:
            return lhs +'==' + rhs

        if op.is_ne or op.is_ne2:
            return lhs +'!=' + rhs

        if op.is_ge:
            return lhs +'>=' + rhs

        if op.is_gt:
            return lhs +'>' + rhs

        raise RuntimeError('Cannot determine comparison operator!')

    def print_bit_operator(self, op: ASTBitOperator, prefix: str = "") -> str:
        """
        Converts a bit operator in NEST syntax.
        :param op: a bit operator object
        :return: a string representation
        """
        lhs = self.print_expression(op.get_lhs(), prefix=prefix)
        rhs = self.print_expression(op.get_rhs(), prefix=prefix)

        if op.is_bit_shift_left:
            return lhs + '<<' + rhs

        if op.is_bit_shift_right:
            return lhs +'>>' + rhs

        if op.is_bit_and:
            return lhs +'&' + rhs

        if op.is_bit_or:
            return lhs +'|' + rhs

        if op.is_bit_xor:
            return lhs +'^' + rhs

        raise RuntimeError('Cannot determine bit operator!')

    def print_arithmetic_operator(self, op: ASTArithmeticOperator, prefix: str = "") -> str:
        """
        Converts an arithmetic operator.
        :param op: an arithmetic operator object
        :return: a string representation
        """
        lhs = self.print_expression(op.get_lhs(), prefix=prefix)
        rhs = self.print_expression(op.get_rhs(), prefix=prefix)

        if op.is_plus_op:
            return lhs + ' + ' + rhs

        if op.is_minus_op:
            return lhs + ' - ' + rhs

        if op.is_times_op:
            return lhs + ' * ' + rhs

        if op.is_div_op:
            return lhs + ' / ' + rhs

        if op.is_modulo_op:
            return lhs + ' %% ' + rhs

        if op.is_pow_op:
            return 'pow' + '(' + lhs + ', ' + rhs + ')'

        raise RuntimeError('Cannot determine arithmetic operator!')

    def print_ternary_operator(self, node: ASTExpression, prefix: str = "") -> str:
        """
        Converts a ternary operator.
        :return: a string representation
        """
        condition = self.print_expression(node.get_condition(), prefix=prefix)
        if_true = self.print_expression(node.get_if_true(), prefix=prefix)
        if_not = self.print_expression(node.if_not, prefix=prefix)

        return '(' + condition + ') ? (' + if_true + ') : (' + if_not + ')'

    def print_binary_op(self, binary_operator: Union[ASTArithmeticOperator, ASTBitOperator, ASTComparisonOperator, ASTLogicalOperator], prefix: str = "") -> str:
        """
        Converts a binary operator.
        :param binary_operator: a binary operator object
        :return: a string representation
        """

        if isinstance(binary_operator, ASTArithmeticOperator):
            return self.print_arithmetic_operator(binary_operator, prefix)

        if isinstance(binary_operator, ASTBitOperator):
            return self.print_bit_operator(binary_operator, prefix)

        if isinstance(binary_operator, ASTComparisonOperator):
            return self.print_comparison_operator(binary_operator, prefix)

        if isinstance(binary_operator, ASTLogicalOperator):
            return self.print_logical_operator(binary_operator, prefix)

        raise RuntimeError('Cannot determine binary operator!')
