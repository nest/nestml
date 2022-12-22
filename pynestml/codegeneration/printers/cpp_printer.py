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
from pynestml.codegeneration.printers.ast_printer import ASTPrinter
from pynestml.meta_model.ast_arithmetic_operator import ASTArithmeticOperator
from pynestml.meta_model.ast_assignment import ASTAssignment
from pynestml.meta_model.ast_bit_operator import ASTBitOperator
from pynestml.meta_model.ast_block import ASTBlock
from pynestml.meta_model.ast_block_with_variables import ASTBlockWithVariables
from pynestml.meta_model.ast_comparison_operator import ASTComparisonOperator
from pynestml.meta_model.ast_compound_stmt import ASTCompoundStmt
from pynestml.meta_model.ast_data_type import ASTDataType
from pynestml.meta_model.ast_declaration import ASTDeclaration
from pynestml.meta_model.ast_elif_clause import ASTElifClause
from pynestml.meta_model.ast_else_clause import ASTElseClause
from pynestml.meta_model.ast_equations_block import ASTEquationsBlock
from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_expression_node import ASTExpressionNode
from pynestml.meta_model.ast_for_stmt import ASTForStmt
from pynestml.meta_model.ast_function import ASTFunction
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.meta_model.ast_if_clause import ASTIfClause
from pynestml.meta_model.ast_if_stmt import ASTIfStmt
from pynestml.meta_model.ast_input_block import ASTInputBlock
from pynestml.meta_model.ast_logical_operator import ASTLogicalOperator
from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_neuron_or_synapse_body import ASTNeuronOrSynapseBody
from pynestml.meta_model.ast_ode_equation import ASTOdeEquation
from pynestml.meta_model.ast_inline_expression import ASTInlineExpression
from pynestml.meta_model.ast_kernel import ASTKernel
from pynestml.meta_model.ast_output_block import ASTOutputBlock
from pynestml.meta_model.ast_parameter import ASTParameter
from pynestml.meta_model.ast_return_stmt import ASTReturnStmt
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.meta_model.ast_small_stmt import ASTSmallStmt
from pynestml.meta_model.ast_stmt import ASTStmt
from pynestml.meta_model.ast_unary_operator import ASTUnaryOperator
from pynestml.meta_model.ast_unit_type import ASTUnitType
from pynestml.meta_model.ast_update_block import ASTUpdateBlock
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.meta_model.ast_while_stmt import ASTWhileStmt
from pynestml.symbols.symbol import SymbolKind
from pynestml.symbols.variable_symbol import VariableSymbol


class CppPrinter(ASTPrinter):
    r"""
    Printer for C++ syntax.
    """

    def __init__(self,
                 expression_printer: ExpressionPrinter):
        self._expression_printer = expression_printer

    def print(self, node: ASTNode) -> str:
        if isinstance(node, ASTArithmeticOperator):
            return self.print_arithmetic_operator(node)

        if isinstance(node, ASTAssignment):
            return self.print_assignment(node)

        if isinstance(node, ASTBitOperator):
            return self.print_bit_operator(node)

        if isinstance(node, ASTBlock):
            return self.print_block(node)

        if isinstance(node, ASTBlockWithVariables):
            return self.print_block_with_variables(node)

        if isinstance(node, ASTNeuronOrSynapseBody):
            return self.print_neuron_or_synapse_body(node)

        if isinstance(node, ASTComparisonOperator):
            return self.print_comparison_operator(node)

        if isinstance(node, ASTCompoundStmt):
            return self.print_compound_stmt(node)

        if isinstance(node, ASTDataType):
            return self.print_data_type(node)

        if isinstance(node, ASTElifClause):
            return self.print_elif_clause(node)

        if isinstance(node, ASTElseClause):
            return self.print_else_clause(node)

        if isinstance(node, ASTEquationsBlock):
            return self.print_equations_block(node)

        if isinstance(node, ASTForStmt):
            return self.print_for_stmt(node)

        if isinstance(node, ASTFunction):
            return self.print_function(node)

        if isinstance(node, ASTIfClause):
            return self.print_if_clause(node)

        if isinstance(node, ASTIfStmt):
            return self.print_if_stmt(node)

        if isinstance(node, ASTInputBlock):
            return self.print_input_block(node)

        if isinstance(node, ASTLogicalOperator):
            return self.print_logical_operator(node)

        if isinstance(node, ASTNeuron):
            return self.print_neuron(node)

        if isinstance(node, ASTOdeEquation):
            return self.print_ode_equation(node)

        if isinstance(node, ASTInlineExpression):
            return self.print_inline_expression(node)

        if isinstance(node, ASTKernel):
            return self.print_kernel(node)

        if isinstance(node, ASTOutputBlock):
            return self.print_output_block(node)

        if isinstance(node, ASTParameter):
            return self.print_parameter(node)

        if isinstance(node, ASTReturnStmt):
            return self.print_return_stmt(node)

        if isinstance(node, ASTSmallStmt):
            return self.print_small_stmt(node)

        if isinstance(node, ASTUnaryOperator):
            return self.print_unary_operator(node)

        if isinstance(node, ASTUnitType):
            return self.print_unit_type(node)

        if isinstance(node, ASTUpdateBlock):
            return self.print_update_block(node)

        if isinstance(node, ASTVariable):
            return self._expression_printer.print(node)

        if isinstance(node, ASTWhileStmt):
            return self.print_while_stmt(node)

        if isinstance(node, ASTStmt):
            return self.print_stmt(node)

        if isinstance(node, ASTDeclaration):
            return self.print_declaration(node)

        if isinstance(node, ASTFunctionCall):
            return self._expression_printer.print(node)

        if isinstance(node, ASTExpression):
            return self._expression_printer.print(node)

        if isinstance(node, ASTSimpleExpression):
            return self._expression_printer._simple_expression_printer.print(node)

        return super().print(node)

    def print_declaration(self, node: ASTDeclaration) -> str:
        assert False, "Not implemented! Template should not call this!"

    def print_small_stmt(self, node) -> str:
        if node.is_assignment():
            return self.print_assignment(node.assignment)

    def print_stmt(self, node) -> str:
        if node.is_small_stmt:
            return self.print_small_stmt(node.small_stmt)

    def print_assignment(self, node) -> str:
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

    def print_comparison_operator(self, for_stmt) -> str:
        """
        Prints a single handed over comparison operator for a for stmt to a Nest processable format.
        :param for_stmt: a single for stmt
        :type for_stmt: ASTForStmt
        :return: a string representation
        """
        step = for_stmt.get_step()
        if step < 0:
            return '>'

        if step > 0:
            return '<'

        return '!='

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
