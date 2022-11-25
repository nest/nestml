# -*- coding: utf-8 -*-
#
# nest_printer.py
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
from pynestml.codegeneration.printers.variable_printer import VariablePrinter
from pynestml.codegeneration.printers.types_printer import TypesPrinter
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
from pynestml.meta_model.ast_input_port import ASTInputPort
from pynestml.meta_model.ast_input_qualifier import ASTInputQualifier
from pynestml.meta_model.ast_logical_operator import ASTLogicalOperator
from pynestml.meta_model.ast_nestml_compilation_unit import ASTNestMLCompilationUnit
from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.meta_model.ast_neuron_or_synapse_body import ASTNeuronOrSynapseBody
from pynestml.meta_model.ast_node import ASTNode
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


class NestPrinter(ASTPrinter):
    r"""
    Printer for NEST C++ syntax.
    """

    def __init__(self,
                 variable_printer: VariablePrinter,
                 types_printer: TypesPrinter,
                 expression_printer: ExpressionPrinter):
        super().__init__(variable_printer=variable_printer,
                         types_printer=types_printer)
        self._expression_printer = expression_printer

    def print(self, node: ASTNode, prefix: str = "") -> str:
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
        if isinstance(node, ASTExpression):
            return self.print_expression(node)
        if isinstance(node, ASTForStmt):
            return self.print_for_stmt(node)
        if isinstance(node, ASTFunction):
            return self.print_function(node)
        if isinstance(node, ASTFunctionCall):
            return self.print_function_call(node)
        if isinstance(node, ASTIfClause):
            return self.print_if_clause(node)
        if isinstance(node, ASTIfStmt):
            return self.print_if_stmt(node)
        if isinstance(node, ASTInputBlock):
            return self.print_input_block(node)
        if isinstance(node, ASTInputPort):
            return self.print_input_port(node)
        if isinstance(node, ASTInputQualifier):
            return self.print_input_qualifier(node)
        if isinstance(node, ASTLogicalOperator):
            return self.print_logical_operator(node)
        if isinstance(node, ASTNestMLCompilationUnit):
            return self.print_compilation_unit(node)
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
        if isinstance(node, ASTSimpleExpression):
            return self.print_simple_expression(node)
        if isinstance(node, ASTSmallStmt):
            return self.print_small_stmt(node)
        if isinstance(node, ASTUnaryOperator):
            return self.print_unary_operator(node)
        if isinstance(node, ASTUnitType):
            return self.print_unit_type(node)
        if isinstance(node, ASTUpdateBlock):
            return self.print_update_block(node)
        if isinstance(node, ASTVariable):
            return self._variable_printer.print_variable(node)
        if isinstance(node, ASTWhileStmt):
            return self.print_while_stmt(node)
        if isinstance(node, ASTStmt):
            return self.print_stmt(node)
        return ''

    def print_input_port(self, node: ASTInputPort) -> str:
        return node.name

    def print_simple_expression(self, node, prefix=""):
        return self.print_expression(node, prefix=prefix)

    def print_small_stmt(self, node, prefix="") -> str:
        if node.is_assignment():
            return self.print_assignment(node.assignment, prefix=prefix)

    def print_stmt(self, node, prefix="") -> str:
        if node.is_small_stmt:
            return self.print_small_stmt(node.small_stmt, prefix=prefix)

    def print_assignment(self, node, prefix="") -> str:
        ret = self._variable_utils.print_symbol_origin(node.lhs) % self._variable_printer.print(node.lhs)
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

    def print_step(self, for_stmt) -> str:
        """
        Prints the step length to a nest processable format.
        :param for_stmt: a single for stmt
        :type for_stmt: ASTForStmt
        :return: a string representation
        """
        assert isinstance(for_stmt, ASTForStmt), \
            '(PyNestML.CodeGenerator.Printer) No or wrong type of for-stmt provided (%s)!' % type(for_stmt)
        return for_stmt.get_step()

    def print_expression(self, node: ASTExpressionNode, prefix: str = "") -> str:
        """
        Prints the handed over rhs to a nest readable format.
        :param node: a single meta_model node.
        :type node: ASTExpressionNode
        :return: the corresponding string representation
        """
        return self._expression_printer.print_expression(node, prefix=prefix)

    def print_function_call(self, node: ASTFunctionCall) -> str:
        """
        Prints a single handed over function call.
        :param node: a single function call.
        :type node: ASTFunctionCall
        :return: the corresponding string representation.
        """
        return self._expression_printer.print(node)
