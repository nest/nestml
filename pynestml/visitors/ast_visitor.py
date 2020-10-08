# -*- coding: utf-8 -*-
#
# ast_visitor.py
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

from pynestml.meta_model.ast_arithmetic_operator import ASTArithmeticOperator
from pynestml.meta_model.ast_assignment import ASTAssignment
from pynestml.meta_model.ast_bit_operator import ASTBitOperator
from pynestml.meta_model.ast_block import ASTBlock
from pynestml.meta_model.ast_block_with_variables import ASTBlockWithVariables
from pynestml.meta_model.ast_body import ASTBody
from pynestml.meta_model.ast_comparison_operator import ASTComparisonOperator
from pynestml.meta_model.ast_compound_stmt import ASTCompoundStmt
from pynestml.meta_model.ast_data_type import ASTDataType
from pynestml.meta_model.ast_declaration import ASTDeclaration
from pynestml.meta_model.ast_elif_clause import ASTElifClause
from pynestml.meta_model.ast_else_clause import ASTElseClause
from pynestml.meta_model.ast_equations_block import ASTEquationsBlock
from pynestml.meta_model.ast_expression import ASTExpression
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


class ASTVisitor(object):
    """
    This class represents a standard implementation of a visitor as used to create concrete instances.
    Attributes:
        real_self (ASTVisitor): The visitor which will be used during the visiting of a node.
    """

    def __init__(self):
        """
        Standard constructor.
        """
        self.real_self = self
        return

    def visit_compilation_unit(self, node):
        """
        Visits a single compilation unit, thus all neurons.
        :param node: a single compilation unit.
        :type node: ASTNestMLCompilationUnit
        """
        return

    def visit_neuron(self, node):
        """
        Used to visit a single neuron.
        :return: a single neuron.
        :rtype: ASTNeuron
        """
        return

    def visit_body(self, node):
        """
        Used to visit a single neuron body.
        :param node: a single body element.
        :type node: ASTBody
        """
        return

    def visit_function(self, node):
        """
        Used to visit a single function block.
        :param node: a function block object.
        :type node: ASTFunction
        """
        return

    def visit_update_block(self, node):
        """
        Used to visit a single update block.
        :param node: an update block object.
        :type node: ASTDynamics
        """
        return

    def visit_block(self, node):
        """
        Used to visit a single block of statements.
        :param node: a block object.
        :type node: ASTBlock
        """
        return

    def visit_small_stmt(self, node):
        """
        Used to visit a single small statement.
        :param node: a single small statement.
        :type node: ASTSmallStatement
        """
        return

    def visit_compound_stmt(self, node):
        """
        Used to visit a single compound statement.
        :param node: a single compound statement.
        :type node: ASTCompoundStatement
        """
        return

    def visit_assignment(self, node):
        """
        Used to visit a single assignment.
        :param node: an assignment object.
        :type node: ASTAssignment
        """
        return

    def visit_function_call(self, node):
        """
        Private method: Used to visit a single function call and update its corresponding scope.
        :param node: a function call object.
        :type node: ASTFunctionCall
        """
        return

    def visit_declaration(self, node):
        """
        Used to visit a single declaration.
        :param node: a declaration object.
        :type node: ASTDeclaration
        """
        return

    def visit_return_stmt(self, node):
        """
        Used to visit a single return statement.
        :param node: a return statement object.
        :type node: ASTReturnStmt
        """
        return

    def visit_if_stmt(self, node):
        """
        Used to visit a single if-statement.
        :param node: an if-statement object.
        :type node: ASTIfStmt
        """
        return

    def visit_if_clause(self, node):
        """
        Used to visit a single if-clause.
        :param node: an if clause.
        :type node: ASTIfClause
        """
        return

    def visit_elif_clause(self, node):
        """
        Used to visit a single elif-clause.
        :param node: an elif clause.
        :type node: ASTElifClause
        """
        return

    def visit_else_clause(self, node):
        """
        Used to visit a single else-clause.
        :param node: an else clause.
        :type node: ASTElseClause
        """
        return

    def visit_for_stmt(self, node):
        """
        Private method: Used to visit a single for-stmt.
        :param node: a for-statement.
        :type node: ASTForStmt
        """
        return

    def visit_while_stmt(self, node):
        """
        Used to visit a single while-stmt.
        :param node: a while-statement.
        :type node: ASTWhileStmt
        """
        return

    def visit_data_type(self, node):
        """
        Used to visit a single data-type.
        :param node: a data-type.
        :type node: ASTDataType
        """
        return

    def visit_unit_type(self, node):
        """
        Used to visit a single unit-type.
        :param node: a unit type.
        :type node: ASTUnitType
        """
        return

    def visit_expression(self, node):
        """
        Used to visit a single rhs.
        :param node: an rhs.
        :type node: ASTExpression
        """
        return

    def visit_simple_expression(self, node):
        """
        Used to visit a single simple rhs.
        :param node: a simple rhs.
        :type node: ASTSimpleExpression
        """
        return

    def visit_unary_operator(self, node):
        """
        Used to visit a single unary operator.
        :param node: a single unary operator.
        :type node: ASTUnaryOperator
        """
        return

    def visit_bit_operator(self, node):
        """
        Used to visit a single unary operator.
        :param node: a single bit operator.
        :type node: ASTBitOperator
        """
        return

    def visit_comparison_operator(self, node):
        """
        Used to visit a single comparison operator.
        :param node: a single comparison operator.
        :type node: ASTComparisonOperator
        """
        return

    def visit_logical_operator(self, node):
        """
        Used to visit a single logical operator.
        :param node: a single logical operator.
        :type node: ASTLogicalOperator
        """
        return

    def visit_variable(self, node):
        """
        Used to visit a single variable.
        :param node: a single variable.
        :type node: ASTVariable
        """
        return

    def visit_inline_expression(self, node):
        """
        Used to visit a single inline expression.
        :param node: a single inline expression.
        :type node: ASTInlineExpression
        """
        return

    def visit_kernel(self, node):
        """
        Used to visit a single kernel.
        :param node: a single kernel.
        :type node: ASTKernel
        """
        return

    def visit_ode_equation(self, node):
        """
        Used to visit a single ode-equation.
        :param node: a single ode-equation.
        :type node: ASTOdeEquation
        """
        return

    def visit_block_with_variables(self, node):
        """
        Used to visit a single block of variables.
        :param node: a block with declared variables.
        :type node: ASTBlockWithVariables
        """
        return

    def visit_equations_block(self, node):
        """
        Used to visit a single equations block.
        :param node: a single equations block.
        :type node: ASTEquationsBlock
        """
        return

    def visit_input_block(self, node):
        """
        Used to visit a single input block.
        :param node: a single input block.
        :type node: ASTInputBlock
        """
        return

    def visit_output_block(self, node):
        """
        Used to visit a single output block.
        :param node: a single output block.
        :type node: ASTOutputBlock
        """
        return

    def visit_input_port(self, node):
        """
        Used to visit a single input port.
        :param node: a single input port.
        :type node: ASTInputPort
        """
        return

    def visit_input_qualifier(self, node):
        """
        Used to visit a single input port qualifier.
        :param node: a single input port qualifier node.
        :type node: ASTInputQualifier
        """
        return

    def visit_arithmetic_operator(self, node):
        """
        Used to visit a single arithmetic operator.
        :param node: a single arithmetic operator.
        :type node: ASTArithmeticOperator
        """
        return

    def visit_parameter(self, node):
        """
        Used to visit a single parameter.
        :param node: a single parameter.
        :type node: ASTParameter
        """
        return

    def visit_stmt(self, node):
        return

    def endvisit_compilation_unit(self, node):
        """
        Visits a single compilation unit, thus all neurons.
        :param node: a single compilation unit.
        :type node: ASTNestMLCompilationUnit
        """
        return

    def endvisit_neuron(self, node):
        """
        Used to endvisit a single neuron.
        :return: a single neuron.
        :rtype: ASTNeuron
        """
        return

    def endvisit_body(self, node):
        """
        Used to endvisit a single neuron body.
        :param node: a single body element.
        :type node: ASTBody
        """
        return

    def endvisit_function(self, node):
        """
        Used to endvisit a single function block.
        :param node: a function block object.
        :type node: ASTFunction
        """
        return

    def endvisit_update_block(self, node):
        """
        Used to endvisit a single update block.
        :param node: an update block object.
        :type node: ASTDynamics
        """
        return

    def endvisit_block(self, node):
        """
        Used to endvisit a single block of statements.
        :param node: a block object.
        :type node: ASTBlock
        """
        return

    def endvisit_small_stmt(self, node):
        """
        Used to endvisit a single small statement.
        :param node: a single small statement.
        :type node: ASTSmallStatement
        """
        return

    def endvisit_compound_stmt(self, node):
        """
        Used to endvisit a single compound statement.
        :param node: a single compound statement.
        :type node: ASTCompoundStatement
        """
        return

    def endvisit_assignment(self, node):
        """
        Used to endvisit a single assignment.
        :param node: an assignment object.
        :type node: ASTAssignment
        """
        return

    def endvisit_function_call(self, node):
        """
        Private method: Used to endvisit a single function call and update its corresponding scope.
        :param node: a function call object.
        :type node: ASTFunctionCall
        """
        return

    def endvisit_declaration(self, node):
        """
        Used to endvisit a single declaration.
        :param node: a declaration object.
        :type node: ASTDeclaration
        """
        return

    def endvisit_return_stmt(self, node):
        """
        Used to endvisit a single return statement.
        :param node: a return statement object.
        :type node: ASTReturnStmt
        """
        return

    def endvisit_if_stmt(self, node):
        """
        Used to endvisit a single if-statement.
        :param node: an if-statement object.
        :type node: ASTIfStmt
        """
        return

    def endvisit_if_clause(self, node):
        """
        Used to endvisit a single if-clause.
        :param node: an if clause.
        :type node: ASTIfClause
        """
        return

    def endvisit_elif_clause(self, node):
        """
        Used to endvisit a single elif-clause.
        :param node: an elif clause.
        :type node: ASTElifClause
        """
        return

    def endvisit_else_clause(self, node):
        """
        Used to endvisit a single else-clause.
        :param node: an else clause.
        :type node: ASTElseClause
        """
        return

    def endvisit_for_stmt(self, node):
        """
        Private method: Used to endvisit a single for-stmt.
        :param node: a for-statement.
        :type node: ASTForStmt
        """
        return

    def endvisit_while_stmt(self, node):
        """
        Used to endvisit a single while-stmt.
        :param node: a while-statement.
        :type node: ASTWhileStmt
        """
        return

    def endvisit_data_type(self, node):
        """
        Used to endvisit a single data-type.
        :param node: a data-type.
        :type node: ASTDataType
        """
        return

    def endvisit_unit_type(self, node):
        """
        Used to endvisit a single unit-type.
        :param node: a unit type.
        :type node: ASTUnitType
        """
        return

    def endvisit_expression(self, node):
        """
        Used to endvisit a single rhs.
        :param node: an rhs.
        :type node: ASTExpression
        """
        return

    def endvisit_simple_expression(self, node):
        """
        Used to endvisit a single simple rhs.
        :param node: a simple rhs.
        :type node: ASTSimpleExpression
        """
        return

    def endvisit_unary_operator(self, node):
        """
        Used to endvisit a single unary operator.
        :param node: a single unary operator.
        :type node: ASTUnaryOperator
        """
        return

    def endvisit_bit_operator(self, node):
        """
        Used to endvisit a single unary operator.
        :param node: a single bit operator.
        :type node: ASTBitOperator
        """
        return

    def endvisit_comparison_operator(self, node):
        """
        Used to endvisit a single comparison operator.
        :param node: a single comparison operator.
        :type node: ASTComparisonOperator
        """
        return

    def endvisit_logical_operator(self, node):
        """
        Used to endvisit a single logical operator.
        :param node: a single logical operator.
        :type node: ASTLogicalOperator
        """
        return

    def endvisit_variable(self, node):
        """
        Used to endvisit a single variable.
        :param node: a single variable.
        :type node: ASTVariable
        """
        return

    def endvisit_inline_expression(self, node):
        """
        Used to endvisit a single inline expression.
        :param node: a single inline expression
        :type node: ASTInlineExpression
        """
        return

    def endvisit_kernel(self, node):
        """
        Used to endvisit a single kernel.
        :param node: a single kernel.
        :type node: ASTKernel
        """
        return

    def endvisit_ode_equation(self, node):
        """
        Used to endvisit a single ode-equation.
        :param node: a single ode-equation.
        :type node: ASTOdeEquation
        """
        return

    def endvisit_block_with_variables(self, node):
        """
        Used to endvisit a single block of variables.
        :param node: a block with declared variables.
        :type node: ASTBlockWithVariables
        """
        return

    def endvisit_equations_block(self, node):
        """
        Used to endvisit a single equations block.
        :param node: a single equations block.
        :type node: ASTEquationsBlock
        """
        return

    def endvisit_input_block(self, node):
        """
        Used to endvisit a single input block.
        :param node: a single input block.
        :type node: ASTInputBlock
        """
        return

    def endvisit_output_block(self, node):
        """
        Used to endvisit a single output block.
        :param node: a single output block.
        :type node: ASTOutputBlock
        """
        return

    def endvisit_input_port(self, node):
        """
        Used to endvisit a single input port.
        :param node: a single input port.
        :type node: ASTInputPort
        """
        return

    def endvisit_input_qualifier(self, node):
        """
        Used to endvisit a single input port qualifier.
        :param node: a single input port qualifier node.
        :type node: ASTInputQualifer
        """
        return

    def endvisit_arithmetic_operator(self, node):
        """
        Used to endvisit a single arithmetic operator.
        :param node: a single arithmetic operator.
        :type node: ASTArithmeticOperator
        """
        return

    def endvisit_parameter(self, node):
        """
        Used to endvisit a single parameter.
        :param node: a single parameter.
        :type node: ASTParameter
        """
        return

    def endvisit_stmt(self, node):
        """
        Used to endvisit a single stmt.
        :param node: a single stmt
        :return: ASTStmt
        """
        return

    def set_real_self(self, _visitor):
        assert (_visitor is not None and isinstance(_visitor, ASTVisitor))
        self.real_self = _visitor
        return

    def get_real_self(self):
        return self.real_self

    def handle(self, _node):
        self.get_real_self().visit(_node)
        self.get_real_self().traverse(_node)
        self.get_real_self().endvisit(_node)
        return

    def visit(self, node):
        """
        Dispatcher for visitor pattern.
        :param node: The ASTElement to visit
        :type node:  ASTElement or inherited
        """
        if isinstance(node, ASTArithmeticOperator):
            self.visit_arithmetic_operator(node)
            return
        if isinstance(node, ASTAssignment):
            self.visit_assignment(node)
            return
        if isinstance(node, ASTBitOperator):
            self.visit_bit_operator(node)
            return
        if isinstance(node, ASTBlock):
            self.visit_block(node)
            return
        if isinstance(node, ASTBlockWithVariables):
            self.visit_block_with_variables(node)
            return
        if isinstance(node, ASTBody):
            self.visit_body(node)
            return
        if isinstance(node, ASTComparisonOperator):
            self.visit_comparison_operator(node)
            return
        if isinstance(node, ASTCompoundStmt):
            self.visit_compound_stmt(node)
            return
        if isinstance(node, ASTDataType):
            self.visit_data_type(node)
            return
        if isinstance(node, ASTDeclaration):
            self.visit_declaration(node)
            return
        if isinstance(node, ASTElifClause):
            self.visit_elif_clause(node)
            return
        if isinstance(node, ASTElseClause):
            self.visit_else_clause(node)
            return
        if isinstance(node, ASTEquationsBlock):
            self.visit_equations_block(node)
            return
        if isinstance(node, ASTExpression):
            self.visit_expression(node)
            return
        if isinstance(node, ASTForStmt):
            self.visit_for_stmt(node)
            return
        if isinstance(node, ASTFunction):
            self.visit_function(node)
            return
        if isinstance(node, ASTFunctionCall):
            self.visit_function_call(node)
            return
        if isinstance(node, ASTIfClause):
            self.visit_if_clause(node)
            return
        if isinstance(node, ASTIfStmt):
            self.visit_if_stmt(node)
            return
        if isinstance(node, ASTInputBlock):
            self.visit_input_block(node)
            return
        if isinstance(node, ASTInputPort):
            self.visit_input_port(node)
            return
        if isinstance(node, ASTInputQualifier):
            self.visit_input_qualifier(node)
            return
        if isinstance(node, ASTLogicalOperator):
            self.visit_logical_operator(node)
            return
        if isinstance(node, ASTNestMLCompilationUnit):
            self.visit_compilation_unit(node)
            return
        if isinstance(node, ASTNeuron):
            self.visit_neuron(node)
            return
        if isinstance(node, ASTOdeEquation):
            self.visit_ode_equation(node)
            return
        if isinstance(node, ASTInlineExpression):
            self.visit_inline_expression(node)
            return
        if isinstance(node, ASTKernel):
            self.visit_kernel(node)
            return
        if isinstance(node, ASTOutputBlock):
            self.visit_output_block(node)
            return
        if isinstance(node, ASTParameter):
            self.visit_parameter(node)
            return
        if isinstance(node, ASTReturnStmt):
            self.visit_return_stmt(node)
            return
        if isinstance(node, ASTSimpleExpression):
            self.visit_simple_expression(node)
            return
        if isinstance(node, ASTSmallStmt):
            self.visit_small_stmt(node)
            return
        if isinstance(node, ASTUnaryOperator):
            self.visit_unary_operator(node)
            return
        if isinstance(node, ASTUnitType):
            self.visit_unit_type(node)
            return
        if isinstance(node, ASTUpdateBlock):
            self.visit_update_block(node)
            return
        if isinstance(node, ASTVariable):
            self.visit_variable(node)
            return
        if isinstance(node, ASTWhileStmt):
            self.visit_while_stmt(node)
            return
        if isinstance(node, ASTStmt):
            self.visit_stmt(node)
            return
        return

    def traverse(self, node):
        """
        Dispatcher for traverse method.
        :param node: The ASTElement to visit
        :type node: Inherited from ASTElement
        """
        if isinstance(node, ASTArithmeticOperator):
            self.traverse_arithmetic_operator(node)
            return
        if isinstance(node, ASTAssignment):
            self.traverse_assignment(node)
            return
        if isinstance(node, ASTBitOperator):
            self.traverse_bit_operator(node)
            return
        if isinstance(node, ASTBlock):
            self.traverse_block(node)
            return
        if isinstance(node, ASTBlockWithVariables):
            self.traverse_block_with_variables(node)
            return
        if isinstance(node, ASTBody):
            self.traverse_body(node)
            return
        if isinstance(node, ASTComparisonOperator):
            self.traverse_comparison_operator(node)
            return
        if isinstance(node, ASTCompoundStmt):
            self.traverse_compound_stmt(node)
            return
        if isinstance(node, ASTDataType):
            self.traverse_data_type(node)
            return
        if isinstance(node, ASTDeclaration):
            self.traverse_declaration(node)
            return
        if isinstance(node, ASTElifClause):
            self.traverse_elif_clause(node)
            return
        if isinstance(node, ASTElseClause):
            self.traverse_else_clause(node)
            return
        if isinstance(node, ASTEquationsBlock):
            self.traverse_equations_block(node)
            return
        if isinstance(node, ASTExpression):
            self.traverse_expression(node)
            return
        if isinstance(node, ASTForStmt):
            self.traverse_for_stmt(node)
            return
        if isinstance(node, ASTFunction):
            self.traverse_function(node)
            return
        if isinstance(node, ASTFunctionCall):
            self.traverse_function_call(node)
            return
        if isinstance(node, ASTIfClause):
            self.traverse_if_clause(node)
            return
        if isinstance(node, ASTIfStmt):
            self.traverse_if_stmt(node)
            return
        if isinstance(node, ASTInputBlock):
            self.traverse_input_block(node)
            return
        if isinstance(node, ASTInputPort):
            self.traverse_input_port(node)
            return
        if isinstance(node, ASTInputQualifier):
            self.traverse_input_qualifier(node)
            return
        if isinstance(node, ASTLogicalOperator):
            self.traverse_logical_operator(node)
            return
        if isinstance(node, ASTNestMLCompilationUnit):
            self.traverse_compilation_unit(node)
            return
        if isinstance(node, ASTNeuron):
            self.traverse_neuron(node)
            return
        if isinstance(node, ASTOdeEquation):
            self.traverse_ode_equation(node)
            return
        if isinstance(node, ASTInlineExpression):
            self.traverse_inline_expression(node)
            return
        if isinstance(node, ASTKernel):
            self.traverse_kernel(node)
            return
        if isinstance(node, ASTOutputBlock):
            self.traverse_output_block(node)
            return
        if isinstance(node, ASTParameter):
            self.traverse_parameter(node)
            return
        if isinstance(node, ASTReturnStmt):
            self.traverse_return_stmt(node)
            return
        if isinstance(node, ASTSimpleExpression):
            self.traverse_simple_expression(node)
            return
        if isinstance(node, ASTSmallStmt):
            self.traverse_small_stmt(node)
            return
        if isinstance(node, ASTUnaryOperator):
            self.traverse_unary_operator(node)
            return
        if isinstance(node, ASTUnitType):
            self.traverse_unit_type(node)
            return
        if isinstance(node, ASTUpdateBlock):
            self.traverse_update_block(node)
            return
        if isinstance(node, ASTVariable):
            self.traverse_variable(node)
            return
        if isinstance(node, ASTWhileStmt):
            self.traverse_while_stmt(node)
            return
        if isinstance(node, ASTStmt):
            self.traverse_stmt(node)
            return
        return

    def endvisit(self, node):
        """
        Dispatcher for endvisit.
        :param node: The ASTElement to endvisit
        :type node:  ASTElement or inherited
        """
        if isinstance(node, ASTArithmeticOperator):
            self.endvisit_arithmetic_operator(node)
            return
        if isinstance(node, ASTAssignment):
            self.endvisit_assignment(node)
            return
        if isinstance(node, ASTBitOperator):
            self.endvisit_bit_operator(node)
            return
        if isinstance(node, ASTBlock):
            self.endvisit_block(node)
            return
        if isinstance(node, ASTBlockWithVariables):
            self.endvisit_block_with_variables(node)
            return
        if isinstance(node, ASTBody):
            self.endvisit_body(node)
            return
        if isinstance(node, ASTComparisonOperator):
            self.endvisit_comparison_operator(node)
            return
        if isinstance(node, ASTCompoundStmt):
            self.endvisit_compound_stmt(node)
            return
        if isinstance(node, ASTDataType):
            self.endvisit_data_type(node)
            return
        if isinstance(node, ASTDeclaration):
            self.endvisit_declaration(node)
            return
        if isinstance(node, ASTElifClause):
            self.endvisit_elif_clause(node)
            return
        if isinstance(node, ASTElseClause):
            self.endvisit_else_clause(node)
            return
        if isinstance(node, ASTEquationsBlock):
            self.endvisit_equations_block(node)
            return
        if isinstance(node, ASTExpression):
            self.endvisit_expression(node)
            return
        if isinstance(node, ASTForStmt):
            self.endvisit_for_stmt(node)
            return
        if isinstance(node, ASTFunction):
            self.endvisit_function(node)
            return
        if isinstance(node, ASTFunctionCall):
            self.endvisit_function_call(node)
            return
        if isinstance(node, ASTIfClause):
            self.endvisit_if_clause(node)
            return
        if isinstance(node, ASTIfStmt):
            self.endvisit_if_stmt(node)
            return
        if isinstance(node, ASTInputBlock):
            self.endvisit_input_block(node)
            return
        if isinstance(node, ASTInputPort):
            self.endvisit_input_port(node)
            return
        if isinstance(node, ASTInputQualifier):
            self.endvisit_input_qualifier(node)
            return
        if isinstance(node, ASTLogicalOperator):
            self.endvisit_logical_operator(node)
            return
        if isinstance(node, ASTNestMLCompilationUnit):
            self.endvisit_compilation_unit(node)
            return
        if isinstance(node, ASTNeuron):
            self.endvisit_neuron(node)
            return
        if isinstance(node, ASTOdeEquation):
            self.endvisit_ode_equation(node)
            return
        if isinstance(node, ASTInlineExpression):
            self.endvisit_inline_expression(node)
            return
        if isinstance(node, ASTKernel):
            self.endvisit_kernel(node)
            return
        if isinstance(node, ASTOutputBlock):
            self.endvisit_output_block(node)
            return
        if isinstance(node, ASTParameter):
            self.endvisit_parameter(node)
            return
        if isinstance(node, ASTReturnStmt):
            self.endvisit_return_stmt(node)
            return
        if isinstance(node, ASTSimpleExpression):
            self.endvisit_simple_expression(node)
            return
        if isinstance(node, ASTSmallStmt):
            self.endvisit_small_stmt(node)
            return
        if isinstance(node, ASTUnaryOperator):
            self.endvisit_unary_operator(node)
            return
        if isinstance(node, ASTUnitType):
            self.endvisit_unit_type(node)
            return
        if isinstance(node, ASTUpdateBlock):
            self.endvisit_update_block(node)
            return
        if isinstance(node, ASTVariable):
            self.endvisit_variable(node)
            return
        if isinstance(node, ASTWhileStmt):
            self.endvisit_while_stmt(node)
            return
        if isinstance(node, ASTStmt):
            self.endvisit_stmt(node)
            return
        return

    def traverse_arithmetic_operator(self, node):
        return

    def traverse_assignment(self, node):
        if node.get_variable() is not None:
            node.get_variable().accept(self.get_real_self())
        if node.get_expression() is not None:
            node.get_expression().accept(self.get_real_self())
        return

    def traverse_bit_operator(self, node):
        return

    def traverse_block(self, node):
        if node.get_stmts() is not None:
            for sub_node in node.get_stmts():
                sub_node.accept(self.get_real_self())
        return

    def traverse_block_with_variables(self, _node):
        if _node.get_declarations() is not None:
            for sub_node in _node.get_declarations():
                sub_node.accept(self.get_real_self())
        return

    def traverse_body(self, node):
        if node.get_body_elements() is not None:
            for sub_node in node.get_body_elements():
                sub_node.accept(self.get_real_self())
        return

    def traverse_comparison_operator(self, node):
        return

    def traverse_compound_stmt(self, node):
        if node.get_if_stmt() is not None:
            node.get_if_stmt().accept(self.get_real_self())
        if node.get_while_stmt() is not None:
            node.get_while_stmt().accept(self.get_real_self())
        if node.get_for_stmt() is not None:
            node.get_for_stmt().accept(self.get_real_self())
        return

    def traverse_data_type(self, node):
        if node.get_unit_type() is not None:
            node.get_unit_type().accept(self.get_real_self())
        return

    def traverse_declaration(self, node):
        if node.get_variables() is not None:
            for sub_node in node.get_variables():
                sub_node.accept(self.get_real_self())
        if node.get_data_type() is not None:
            node.get_data_type().accept(self.get_real_self())
        if node.get_expression() is not None:
            node.get_expression().accept(self.get_real_self())
        if node.get_invariant() is not None:
            node.get_invariant().accept(self.get_real_self())
        return

    def traverse_elif_clause(self, node):
        if node.get_condition() is not None:
            node.get_condition().accept(self.get_real_self())
        if node.get_block() is not None:
            node.get_block().accept(self.get_real_self())
        return

    def traverse_else_clause(self, node):
        if node.get_block() is not None:
            node.get_block().accept(self.get_real_self())
        return

    def traverse_equations_block(self, node):
        if node.get_declarations() is not None:
            for sub_node in node.get_declarations():
                sub_node.accept(self.get_real_self())
        return

    def traverse_expression(self, node):
        if node.get_expression() is not None:
            node.get_expression().accept(self.get_real_self())
        if node.get_unary_operator() is not None:
            node.get_unary_operator().accept(self.get_real_self())
        if node.get_binary_operator() is not None:
            node.get_binary_operator().accept(self.get_real_self())
        if node.get_lhs() is not None:
            node.get_lhs().accept(self.get_real_self())
        if node.get_rhs() is not None:
            node.get_rhs().accept(self.get_real_self())
        if node.get_condition() is not None:
            node.get_condition().accept(self.get_real_self())
        if node.get_if_true() is not None:
            node.get_if_true().accept(self.get_real_self())
        if node.get_if_not() is not None:
            node.get_if_not().accept(self.get_real_self())

    def traverse_for_stmt(self, node):
        if node.get_start_from() is not None:
            node.get_start_from().accept(self.get_real_self())
        if node.get_end_at() is not None:
            node.get_end_at().accept(self.get_real_self())
        if node.get_block() is not None:
            node.get_block().accept(self.get_real_self())
        return

    def traverse_function(self, node):
        if node.get_parameters() is not None:
            for sub_node in node.get_parameters():
                sub_node.accept(self.get_real_self())
        if node.get_return_type() is not None:
            node.get_return_type().accept(self.get_real_self())
        if node.get_block() is not None:
            node.get_block().accept(self.get_real_self())
        return

    def traverse_function_call(self, node):
        if node.get_args() is not None:
            for sub_node in node.get_args():
                sub_node.accept(self.get_real_self())
        return

    def traverse_if_clause(self, node):
        if node.get_condition() is not None:
            node.get_condition().accept(self.get_real_self())
        if node.get_block() is not None:
            node.get_block().accept(self.get_real_self())
        return

    def traverse_if_stmt(self, node):
        if node.get_if_clause() is not None:
            node.get_if_clause().accept(self.get_real_self())
        for elifClause in node.get_elif_clauses():
            elifClause.accept(self.get_real_self())
        if node.get_else_clause() is not None:
            node.get_else_clause().accept(self.get_real_self())
        return

    def traverse_input_block(self, node):
        if node.get_input_ports() is not None:
            for sub_node in node.get_input_ports():
                sub_node.accept(self.get_real_self())
        return

    def traverse_input_port(self, node):
        if node.get_input_qualifiers() is not None:
            for sub_node in node.get_input_qualifiers():
                sub_node.accept(self.get_real_self())
        return

    def traverse_input_qualifier(self, node):
        return

    def traverse_logical_operator(self, node):
        return

    def traverse_compilation_unit(self, node):
        if node.get_neuron_list() is not None:
            for sub_node in node.get_neuron_list():
                sub_node.accept(self.get_real_self())
        return

    def traverse_neuron(self, node):
        if node.get_body() is not None:
            node.get_body().accept(self.get_real_self())
        return

    def traverse_ode_equation(self, node):
        if node.get_lhs() is not None:
            node.get_lhs().accept(self.get_real_self())
        if node.get_rhs() is not None:
            node.get_rhs().accept(self.get_real_self())
        return

    def traverse_inline_expression(self, node):
        if node.get_data_type() is not None:
            node.get_data_type().accept(self.get_real_self())
        if node.get_expression() is not None:
            node.get_expression().accept(self.get_real_self())
        return

    def traverse_kernel(self, node):
        for var, expr in zip(node.get_variables(), node.get_expressions()):
            var.accept(self.get_real_self())
            expr.accept(self.get_real_self())
        return

    def traverse_output_block(self, node):
        return

    def traverse_parameter(self, node):
        if node.get_data_type() is not None:
            node.get_data_type().accept(self.get_real_self())
        return

    def traverse_return_stmt(self, node):
        if node.get_expression() is not None:
            node.get_expression().accept(self.get_real_self())
        return

    def traverse_simple_expression(self, node):
        if node.get_function_call() is not None:
            node.get_function_call().accept(self.get_real_self())
        if node.get_variable() is not None:
            node.get_variable().accept(self.get_real_self())
        return

    def traverse_small_stmt(self, node):
        if node.get_assignment() is not None:
            node.get_assignment().accept(self.get_real_self())
        if node.get_function_call() is not None:
            node.get_function_call().accept(self.get_real_self())
        if node.get_declaration() is not None:
            node.get_declaration().accept(self.get_real_self())
        if node.get_return_stmt() is not None:
            node.get_return_stmt().accept(self.get_real_self())
        return

    def traverse_unary_operator(self, _node):
        return

    def traverse_unit_type(self, node):
        if node.base is not None:
            node.base.accept(self.get_real_self())
        if node.get_lhs() is not None:
            if isinstance(node.get_lhs(), ASTUnitType):
                node.get_lhs().accept(self.get_real_self())
        if node.get_rhs() is not None:
            node.get_rhs().accept(self.get_real_self())
        if node.compound_unit is not None:
            node.compound_unit.accept(self.get_real_self())
        return

    def traverse_update_block(self, node):
        if node.get_block() is not None:
            node.get_block().accept(self.get_real_self())
        return

    def traverse_variable(self, node):
        return

    def traverse_while_stmt(self, node):
        if node.get_condition() is not None:
            node.get_condition().accept(self.get_real_self())
        if node.get_block() is not None:
            node.get_block().accept(self.get_real_self())
        return

    def traverse_stmt(self, node):
        if node.is_small_stmt():
            node.small_stmt.accept(self.get_real_self())
        if node.is_compound_stmt():
            node.compound_stmt.accept(self.get_real_self())
