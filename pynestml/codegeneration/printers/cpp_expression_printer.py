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

from typing import Tuple

from pynestml.codegeneration.printers.expression_printer import ExpressionPrinter
from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_expression_node import ASTExpressionNode
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.utils.ast_utils import ASTUtils


class CppExpressionPrinter(ExpressionPrinter):
    r"""
    Expressions printer for C++.
    """

    def print_expression(self, node: ASTExpressionNode, prefix: str = ""):
        """Print an expression.

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
            return str(node.get_implicit_conversion_factor()) + " * (" + self.__do_print(node, prefix=prefix) + ")"

        return self.__do_print(node, prefix=prefix)

    def __do_print(self, node: ASTExpressionNode, prefix: str="") -> str:
        if isinstance(node, ASTSimpleExpression):
            if node.has_unit():
                return str(node.get_numeric_literal()) + "*" + \
                    self.reference_converter.convert_name_reference(node.get_variable(), prefix=prefix)

            if node.is_numeric_literal():
                return str(node.get_numeric_literal())

            if node.is_inf_literal:
                return self.reference_converter.convert_constant("inf")

            if node.is_string():
                return str(node.get_string())

            if node.is_boolean_true:
                return self.reference_converter.convert_constant("true")

            if node.is_boolean_false:
                return self.reference_converter.convert_constant("false")

            if node.is_variable():
                return self.reference_converter.convert_name_reference(node.get_variable(), prefix=prefix)

            if node.is_function_call():
                return self.print_function_call(node.get_function_call(), prefix=prefix)

            raise Exception("Unknown node type")

        if isinstance(node, ASTExpression):
            # a unary operator
            if node.is_unary_operator():
                op = self.reference_converter.convert_unary_op(node.get_unary_operator())
                rhs = self.print_expression(node.get_expression(), prefix=prefix)
                return op % rhs

            # encapsulated in brackets
            if node.is_encapsulated:
                return self.reference_converter.convert_encapsulated() % self.print_expression(node.get_expression(),
                                                                                               prefix=prefix)

            # logical not
            if node.is_logical_not:
                op = self.reference_converter.convert_logical_not()
                rhs = self.print_expression(node.get_expression(), prefix=prefix)
                return op % rhs

            # compound rhs with lhs + rhs
            if node.is_compound_expression():
                lhs = self.print_expression(node.get_lhs(), prefix=prefix)
                op = self.reference_converter.convert_binary_op(node.get_binary_operator())
                rhs = self.print_expression(node.get_rhs(), prefix=prefix)
                return op % (lhs, rhs)

            if node.is_ternary_operator():
                condition = self.print_expression(node.get_condition(), prefix=prefix)
                if_true = self.print_expression(node.get_if_true(), prefix=prefix)
                if_not = self.print_expression(node.if_not, prefix=prefix)
                return self.reference_converter.convert_ternary_operator() % (condition, if_true, if_not)

            raise Exception("Unknown node type")

        raise RuntimeError("Tried to print unknown expression: \"%s\"" % str(node))

    def print_function_call(self, function_call: ASTFunctionCall, prefix: str = "") -> str:
        """Print a function call, including bracketed arguments list.

        Parameters
        ----------
        node
            The function call node to print.
        prefix
            Optional string that will be prefixed to the function call. For example, to refer to a function call in the class "node", use a prefix equal to "node." or "node->".

            Predefined functions will not be prefixed.

        Returns
        -------
        s
            The function call string.
        """
        function_name = self.reference_converter.convert_function_call(function_call, prefix=prefix)
        if ASTUtils.needs_arguments(function_call):
            if function_call.get_name() == PredefinedFunctions.PRINT or function_call.get_name() == PredefinedFunctions.PRINTLN:
                return function_name.format(self.reference_converter.convert_print_statement(function_call))

            return function_name.format(*self.print_function_call_argument_list(function_call, prefix=prefix))

        return function_name

    def print_function_call_argument_list(self, function_call: ASTFunctionCall, prefix: str="") -> Tuple[str, ...]:
        ret = []

        for arg in function_call.get_args():
            ret.append(self.print_expression(arg, prefix=prefix))

        return tuple(ret)
