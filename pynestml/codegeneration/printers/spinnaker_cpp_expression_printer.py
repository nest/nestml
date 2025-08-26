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
from pynestml.codegeneration.printers.cpp_expression_printer import CppExpressionPrinter
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

class SpiNNakerCppExpressionPrinter(CppExpressionPrinter):
    r"""
    Printer for ``ASTExpression`` nodes in C++ syntax.
    """

    def _print_arithmetic_operator_expression(self, node: ASTExpressionNode) -> str:
        """
        Prints an arithmetic operator.
        :param node: an expression with arithmetic operator
        :return: a string representation
        """
        op = node.get_binary_operator()

        lhs = self.print(node.get_lhs())
        rhs = self.print(node.get_rhs())

        if op.is_pow_op:
            # TODO: make a dummy ASTFunctionCall so we can delegate this to the FunctionCallPrinter
            return "(expk(" + rhs + " * logk(" + lhs + ")))"

        if op.is_plus_op:
            return lhs + " + " + rhs

        if op.is_minus_op:
            return lhs + " - " + rhs

        if op.is_times_op:
#            return "(" + lhs + " * " + rhs + " >> 16)"
            return lhs + " * " + rhs

        if op.is_div_op:
            raise Exception("SpiNNaker does not feature an FPU so division is not implemented on this platform")
            #return lhs + " / " + rhs

        if op.is_modulo_op:
            return lhs + " % " + rhs

        raise RuntimeError("Cannot determine arithmetic operator!")
