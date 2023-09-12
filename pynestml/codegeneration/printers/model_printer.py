# -*- coding: utf-8 -*-
#
# model_printer.py
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

from pynestml.codegeneration.printers.ast_printer import ASTPrinter
from pynestml.meta_model.ast_arithmetic_operator import ASTArithmeticOperator
from pynestml.meta_model.ast_assignment import ASTAssignment
from pynestml.meta_model.ast_bit_operator import ASTBitOperator
from pynestml.meta_model.ast_block import ASTBlock
from pynestml.meta_model.ast_block_with_variables import ASTBlockWithVariables
from pynestml.meta_model.ast_compound_stmt import ASTCompoundStmt
from pynestml.meta_model.ast_data_type import ASTDataType
from pynestml.meta_model.ast_declaration import ASTDeclaration
from pynestml.meta_model.ast_elif_clause import ASTElifClause
from pynestml.meta_model.ast_else_clause import ASTElseClause
from pynestml.meta_model.ast_equations_block import ASTEquationsBlock
from pynestml.meta_model.ast_for_stmt import ASTForStmt
from pynestml.meta_model.ast_function import ASTFunction
from pynestml.meta_model.ast_if_clause import ASTIfClause
from pynestml.meta_model.ast_if_stmt import ASTIfStmt
from pynestml.meta_model.ast_input_block import ASTInputBlock
from pynestml.meta_model.ast_input_qualifier import ASTInputQualifier
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
from pynestml.meta_model.ast_small_stmt import ASTSmallStmt
from pynestml.meta_model.ast_stmt import ASTStmt
from pynestml.meta_model.ast_synapse import ASTSynapse
from pynestml.meta_model.ast_unary_operator import ASTUnaryOperator
from pynestml.meta_model.ast_unit_type import ASTUnitType
from pynestml.meta_model.ast_update_block import ASTUpdateBlock
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.meta_model.ast_while_stmt import ASTWhileStmt
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.meta_model.ast_comparison_operator import ASTComparisonOperator
from pynestml.meta_model.ast_input_port import ASTInputPort
from pynestml.meta_model.ast_nestml_compilation_unit import ASTNestMLCompilationUnit
from pynestml.meta_model.ast_on_receive_block import ASTOnReceiveBlock


class ModelPrinter(ASTPrinter):
    r"""
    Generic base class for printing any ASTNode.
    """

    def print_arithmetic_operator(self, node: ASTArithmeticOperator) -> str:
        raise Exception("Printer does not support printing this node type")

    def print_assignment(self, node: ASTAssignment) -> str:
        raise Exception("Printer does not support printing this node type")

    def print_bit_operator(self, node: ASTBitOperator) -> str:
        raise Exception("Printer does not support printing this node type")

    def print_block(self, node: ASTBlock) -> str:
        raise Exception("Printer does not support printing this node type")

    def print_block_with_variables(self, node: ASTBlockWithVariables) -> str:
        raise Exception("Printer does not support printing this node type")

    def print_neuron_or_synapse_body(self, node: ASTNeuronOrSynapseBody) -> str:
        raise Exception("Printer does not support printing this node type")

    def print_comparison_operator(self, node: ASTComparisonOperator) -> str:
        raise Exception("Printer does not support printing this node type")

    def print_compound_stmt(self, node: ASTCompoundStmt) -> str:
        raise Exception("Printer does not support printing this node type")

    def print_data_type(self, node: ASTDataType) -> str:
        raise Exception("Printer does not support printing this node type")

    def print_elif_clause(self, node: ASTElifClause) -> str:
        raise Exception("Printer does not support printing this node type")

    def print_else_clause(self, node: ASTElseClause) -> str:
        raise Exception("Printer does not support printing this node type")

    def print_equations_block(self, node: ASTEquationsBlock) -> str:
        raise Exception("Printer does not support printing this node type")

    def print_for_stmt(self, node: ASTForStmt) -> str:
        raise Exception("Printer does not support printing this node type")

    def print_function(self, node: ASTFunction) -> str:
        raise Exception("Printer does not support printing this node type")

    def print_if_clause(self, node: ASTIfClause) -> str:
        raise Exception("Printer does not support printing this node type")

    def print_if_stmt(self, node: ASTIfStmt) -> str:
        raise Exception("Printer does not support printing this node type")

    def print_input_block(self, node: ASTInputBlock) -> str:
        raise Exception("Printer does not support printing this node type")

    def print_input_port(self, node: ASTInputPort) -> str:
        raise Exception("Printer does not support printing this node type")

    def print_input_qualifier(self, node: ASTInputQualifier) -> str:
        raise Exception("Printer does not support printing this node type")

    def print_logical_operator(self, node: ASTLogicalOperator) -> str:
        raise Exception("Printer does not support printing this node type")

    def print_compilation_unit(self, node: ASTNestMLCompilationUnit) -> str:
        raise Exception("Printer does not support printing this node type")

    def print_neuron(self, node: ASTNeuron) -> str:
        raise Exception("Printer does not support printing this node type")

    def print_ode_equation(self, node: ASTOdeEquation) -> str:
        raise Exception("Printer does not support printing this node type")

    def print_inline_expression(self, node: ASTInlineExpression) -> str:
        raise Exception("Printer does not support printing this node type")

    def print_kernel(self, node: ASTKernel) -> str:
        raise Exception("Printer does not support printing this node type")

    def print_output_block(self, node: ASTOutputBlock) -> str:
        raise Exception("Printer does not support printing this node type")

    def print_on_receive_block(self, node: ASTOnReceiveBlock) -> str:
        raise Exception("Printer does not support printing this node type")

    def print_parameter(self, node: ASTParameter) -> str:
        raise Exception("Printer does not support printing this node type")

    def print_return_stmt(self, node: ASTReturnStmt) -> str:
        raise Exception("Printer does not support printing this node type")

    def print_small_stmt(self, node: ASTSmallStmt) -> str:
        raise Exception("Printer does not support printing this node type")

    def print_unary_operator(self, node: ASTUnaryOperator) -> str:
        raise Exception("Printer does not support printing this node type")

    def print_unit_type(self, node: ASTUnitType) -> str:
        raise Exception("Printer does not support printing this node type")

    def print_update_block(self, node: ASTUpdateBlock) -> str:
        raise Exception("Printer does not support printing this node type")

    def print_while_stmt(self, node: ASTWhileStmt) -> str:
        raise Exception("Printer does not support printing this node type")

    def print_stmt(self, node: ASTStmt) -> str:
        raise Exception("Printer does not support printing this node type")

    def print_synapse(self, node: ASTSynapse) -> str:
        raise Exception("Printer does not support printing this node type")

    def print_declaration(self, node: ASTDeclaration) -> str:
        raise Exception("Printer does not support printing this node type")

    def print_variable(self, node: ASTVariable) -> str:
        raise Exception("Printer does not support printing this node type")

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

        if isinstance(node, ASTComparisonOperator):
            return self.print_comparison_operator(node)

        if isinstance(node, ASTCompoundStmt):
            return self.print_compound_stmt(node)

        if isinstance(node, ASTDataType):
            return self.print_data_type(node)

        if isinstance(node, ASTDeclaration):
            return self.print_declaration(node)

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

        if isinstance(node, ASTInlineExpression):
            return self.print_inline_expression(node)

        if isinstance(node, ASTInputBlock):
            return self.print_input_block(node)

        if isinstance(node, ASTInputPort):
            return self.print_input_port(node)

        if isinstance(node, ASTInputQualifier):
            return self.print_input_qualifier(node)

        if isinstance(node, ASTKernel):
            return self.print_kernel(node)

        if isinstance(node, ASTLogicalOperator):
            return self.print_logical_operator(node)

        if isinstance(node, ASTNestMLCompilationUnit):
            return self.print_compilation_unit(node)

        if isinstance(node, ASTNeuron):
            return self.print_neuron(node)

        if isinstance(node, ASTNeuronOrSynapseBody):
            return self.print_neuron_or_synapse_body(node)

        if isinstance(node, ASTOdeEquation):
            return self.print_ode_equation(node)

        if isinstance(node, ASTOnReceiveBlock):
            return self.print_on_receive_block(node)

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

        if isinstance(node, ASTStmt):
            return self.print_stmt(node)

        if isinstance(node, ASTSynapse):
            return self.print_synapse(node)

        if isinstance(node, ASTUnaryOperator):
            return self.print_unary_operator(node)

        if isinstance(node, ASTUnitType):
            return self.print_unit_type(node)

        if isinstance(node, ASTUpdateBlock):
            return self.print_update_block(node)

        if isinstance(node, ASTVariable):
            return self.print_variable(node)

        if isinstance(node, ASTWhileStmt):
            return self.print_while_stmt(node)

        raise Exception("Printer does not support printing this node type")
