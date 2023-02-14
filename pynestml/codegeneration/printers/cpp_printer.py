# -*- coding: utf-8 -*-
#
# cpp_printer.py
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
from pynestml.codegeneration.printers.model_printer import ModelPrinter
from pynestml.meta_model.ast_assignment import ASTAssignment
from pynestml.meta_model.ast_expression_node import ASTExpressionNode
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.symbols.symbol import SymbolKind
from pynestml.symbols.variable_symbol import VariableSymbol
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.meta_model.ast_comparison_operator import ASTComparisonOperator


class CppPrinter(ModelPrinter):
    r"""
    This class can be used to print any ASTNode to C++ syntax.
    """

    def __init__(self,
                 expression_printer: ExpressionPrinter):
        self._expression_printer = expression_printer

    def print_comparison_operator(self, node: ASTComparisonOperator) -> str:
        return self._expression_printer.print_comparison_operator(node)

    def print_variable(self, node: ASTVariable) -> str:
        return self._expression_printer.print(node)

    def print_function_call(self, node: ASTFunctionCall) -> str:
        return self._expression_printer.print(node)

    def print_expression(self, node: ASTExpression) -> str:
        return self._expression_printer.print(node)

    def print_simple_expression(self, node: ASTSimpleExpression) -> str:
        return self._expression_printer._simple_expression_printer.print(node)

    def print_small_stmt(self, node) -> str:
        if node.is_assignment():
            return self.print_assignment(node.assignment)

        raise Exception("Could not print node: " + str(node))

    def print_stmt(self, node) -> str:
        if node.is_small_stmt:
            return self.print_small_stmt(node.small_stmt)

        raise Exception("Could not print node: " + str(node))

    def print_assignment(self, node: ASTAssignment) -> str:
        ret = self._expression_printer.print(node.lhs)
        ret += ' '
        if node.is_compound_quotient:
            ret += '/='
        elif node.is_compound_product:
            ret += '*='
        elif node.is_compound_minus:
            ret += '-='
        elif node.is_compound_sum:
            ret += '+='
        else:
            ret += '='

        ret += ' ' + self.print(node.rhs)

        return ret

    def print_delay_parameter(self, variable: VariableSymbol) -> str:
        """
        Prints the delay parameter
        :param variable: Variable with delay parameter
        :return: the corresponding delay parameter
        """
        assert isinstance(variable, VariableSymbol), \
            '(PyNestML.CodeGeneration.Printer) No or wrong type of variable symbol provided (%s)!' % type(variable)
        delay_parameter = variable.get_delay_parameter()
        delay_parameter_var = ASTVariable(delay_parameter, scope=variable.get_corresponding_scope())
        symbol = delay_parameter_var.get_scope().resolve_to_symbol(delay_parameter_var.get_complete_name(),
                                                                   SymbolKind.VARIABLE)
        if symbol is not None:
            # delay parameter is a variable
            return self._expression_printer.print_origin(symbol) + delay_parameter

        return delay_parameter

    def print_expression(self, node: ASTExpressionNode) -> str:
        """
        Prints the handed over rhs to a nest readable format.
        :param node: a single meta_model node.
        :return: the corresponding string representation
        """
        assert isinstance(node, ASTExpressionNode)

        return self._expression_printer.print(node)
