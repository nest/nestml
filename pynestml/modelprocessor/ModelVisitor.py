#
# ModelVisitor.py
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

from pynestml.modelprocessor.ASTArithmeticOperator import ASTArithmeticOperator
from pynestml.modelprocessor.ASTAssignment import ASTAssignment
from pynestml.modelprocessor.ASTBitOperator import ASTBitOperator
from pynestml.modelprocessor.ASTBlock import ASTBlock
from pynestml.modelprocessor.ASTBlockWithVariables import ASTBlockWithVariables
from pynestml.modelprocessor.ASTBody import ASTBody
from pynestml.modelprocessor.ASTComparisonOperator import ASTComparisonOperator
from pynestml.modelprocessor.ASTCompoundStmt import ASTCompoundStmt
from pynestml.modelprocessor.ASTDatatype import ASTDatatype
from pynestml.modelprocessor.ASTDeclaration import ASTDeclaration
from pynestml.modelprocessor.ASTElifClause import ASTElifClause
from pynestml.modelprocessor.ASTElseClause import ASTElseClause
from pynestml.modelprocessor.ASTEquationsBlock import ASTEquationsBlock
from pynestml.modelprocessor.ASTExpression import ASTExpression
from pynestml.modelprocessor.ASTForStmt import ASTForStmt
from pynestml.modelprocessor.ASTFunction import ASTFunction
from pynestml.modelprocessor.ASTFunctionCall import ASTFunctionCall
from pynestml.modelprocessor.ASTIfClause import ASTIfClause
from pynestml.modelprocessor.ASTIfStmt import ASTIfStmt
from pynestml.modelprocessor.ASTInputBlock import ASTInputBlock
from pynestml.modelprocessor.ASTInputLine import ASTInputLine
from pynestml.modelprocessor.ASTInputType import ASTInputType
from pynestml.modelprocessor.ASTLogicalOperator import ASTLogicalOperator
from pynestml.modelprocessor.ASTNESTMLCompilationUnit import ASTNESTMLCompilationUnit
from pynestml.modelprocessor.ASTNeuron import ASTNeuron
from pynestml.modelprocessor.ASTOdeEquation import ASTOdeEquation
from pynestml.modelprocessor.ASTOdeFunction import ASTOdeFunction
from pynestml.modelprocessor.ASTOdeShape import ASTOdeShape
from pynestml.modelprocessor.ASTOutputBlock import ASTOutputBlock
from pynestml.modelprocessor.ASTParameter import ASTParameter
from pynestml.modelprocessor.ASTReturnStmt import ASTReturnStmt
from pynestml.modelprocessor.ASTSimpleExpression import ASTSimpleExpression
from pynestml.modelprocessor.ASTSmallStmt import ASTSmallStmt
from pynestml.modelprocessor.ASTUnaryOperator import ASTUnaryOperator
from pynestml.modelprocessor.ASTUnitType import ASTUnitType
from pynestml.modelprocessor.ASTUpdateBlock import ASTUpdateBlock
from pynestml.modelprocessor.ASTVariable import ASTVariable
from pynestml.modelprocessor.ASTWhileStmt import ASTWhileStmt


class NESTMLVisitor(object):
    """
    This class represents a standard implementation of a visitor as used to create concrete instances.
    Attributes:
        __realSelf (NESTMLVisitor): The visitor which will be used during the visiting of a node.
    """
    __realSelf = None

    def __init__(self):
        """
        Standard constructor.
        """
        self.__realSelf = self
        return

    def visit_compilation_unit(self, _compilation_unit=None):
        """
        Visits a single compilation unit, thus all neurons.
        :param _compilation_unit: a single compilation unit.
        :type _compilation_unit: ASTNESTMLCompilationUnit
        """
        return

    def visit_neuron(self, _neuron=None):
        """
        Used to visit a single neuron.
        :return: a single neuron.
        :rtype: ASTNeuron
        """
        return

    def visit_body(self, _body=None):
        """
        Used to visit a single neuron body.
        :param _body: a single body element.
        :type _body: ASTBody
        """
        return

    def visit_function(self, _block=None):
        """
        Used to visit a single function block.
        :param _block: a function block object.
        :type _block: ASTFunction
        """
        return

    def visit_update_block(self, _block=None):
        """
        Used to visit a single update block.
        :param _block: an update block object. 
        :type _block: ASTDynamics
        """
        return

    def visit_block(self, _block=None):
        """
        Used to visit a single block of statements.
        :param _block: a block object.
        :type _block: ASTBlock
        """
        return

    def visit_small_stmt(self, _stmt=None):
        """
        Used to visit a single small statement.
        :param _stmt: a single small statement.
        :type _stmt: ASTSmallStatement
        """
        return

    def visit_compound_stmt(self, _stmt=None):
        """
        Used to visit a single compound statement.
        :param _stmt: a single compound statement.
        :type _stmt: ASTCompoundStatement
        """
        return

    def visit_assignment(self, _assignment=None):
        """
        Used to visit a single assignment.
        :param _assignment: an assignment object.
        :type _assignment: ASTAssignment
        """
        return

    def visit_function_call(self, _function_call=None):
        """
        Private method: Used to visit a single function call and update its corresponding scope.
        :param _function_call: a function call object.
        :type _function_call: ASTFunctionCall
        """
        return

    def visit_declaration(self, _declaration=None):
        """
        Used to visit a single declaration.
        :param _declaration: a declaration object.
        :type _declaration: ASTDeclaration
        """
        return

    def visit_return_stmt(self, _return_stmt=None):
        """
        Used to visit a single return statement.
        :param _return_stmt: a return statement object.
        :type _return_stmt: ASTReturnStmt
        """
        return

    def visit_if_stmt(self, _if_stmt=None):
        """
        Used to visit a single if-statement.
        :param _if_stmt: an if-statement object.
        :type _if_stmt: ASTIfStmt
        """
        return

    def visit_if_clause(self, _if_clause=None):
        """
        Used to visit a single if-clause.
        :param _if_clause: an if clause.
        :type _if_clause: ASTIfClause
        """
        return

    def visit_elif_clause(self, _elif_clause=None):
        """
        Used to visit a single elif-clause.
        :param _elif_clause: an elif clause.
        :type _elif_clause: ASTElifClause
        """
        return

    def visit_else_clause(self, _else_clause=None):
        """
        Used to visit a single else-clause.
        :param _else_clause: an else clause.
        :type _else_clause: ASTElseClause
        """
        return

    def visit_for_stmt(self, _for_stmt=None):
        """
        Private method: Used to visit a single for-stmt.
        :param _for_stmt: a for-statement.
        :type _for_stmt: ASTForStmt
        """
        return

    def visit_while_stmt(self, _while_stmt=None):
        """
        Used to visit a single while-stmt.
        :param _while_stmt: a while-statement.
        :type _while_stmt: ASTWhileStmt
        """
        return

    def visit_datatype(self, _data_type=None):
        """
        Used to visit a single data-type. 
        :param _data_type: a data-type.
        :type _data_type: ASTDataType
        """
        return

    def visit_unit_type(self, _unit_type=None):
        """
        Used to visit a single unit-type.
        :param _unit_type: a unit type.
        :type _unit_type: ASTUnitType
        """
        return

    def visit_expression(self, _expr=None):
        """
        Used to visit a single expression.
        :param _expr: an expression.
        :type _expr: ASTExpression
        """
        return

    def visit_simple_expression(self, _expr=None):
        """
        Used to visit a single simple expression.
        :param _expr: a simple expression. 
        :type _expr: ASTSimpleExpression
        """
        return

    def visit_unary_operator(self, _unary_op=None):
        """
        Used to visit a single unary operator.
        :param _unary_op: a single unary operator.
        :type _unary_op: ASTUnaryOperator
        """
        return

    def visit_bit_operator(self, _bit_op=None):
        """
        Used to visit a single unary operator.
        :param _bit_op: a single bit operator.
        :type _bit_op: ASTBitOperator
        """
        return

    def visit_comparison_operator(self, _comparison_op=None):
        """
        Used to visit a single comparison operator.
        :param _comparison_op: a single comparison operator.
        :type _comparison_op: ASTComparisonOperator
        """
        return

    def visit_logical_operator(self, _logical_op=None):
        """
        Used to visit a single logical operator.
        :param _logical_op: a single logical operator.
        :type _logical_op: ASTLogicalOperator
        """
        return

    def visit_variable(self, _variable=None):
        """
        Used to visit a single variable.
        :param _variable: a single variable.
        :type _variable: ASTVariable
        """
        return

    def visit_ode_function(self, _ode_function=None):
        """
        Used to visit a single ode-function.
        :param _ode_function: a single ode-function.
        :type _ode_function: ASTOdeFunction
        """
        return

    def visit_ode_shape(self, _ode_shape=None):
        """
        Used to visit a single ode-shape.
        :param _ode_shape: a single ode-shape.
        :type _ode_shape: ASTOdeShape
        """
        return

    def visit_ode_equation(self, _equation=None):
        """
        Used to visit a single ode-equation.
        :param _equation: a single ode-equation.
        :type _equation: ASTOdeEquation
        """
        return

    def visit_block_with_variables(self, _block=None):
        """
        Used to visit a single block of variables.
        :param _block: a block with declared variables.
        :type _block: ASTBlockWithVariables
        """
        return

    def visit_equations_block(self, _block=None):
        """
        Used to visit a single equations block.
        :param _block: a single equations block.
        :type _block: ASTEquationsBlock
        """
        return

    def visit_input_block(self, _block=None):
        """
        Used to visit a single input block.
        :param _block: a single input block.
        :type _block: ASTInputBlock
        """
        return

    def visit_output_block(self, _block=None):
        """
        Used to visit a single output block.
        :param _block: a single output block. 
        :type _block: ASTOutputBlock
        """
        return

    def visit_input_line(self, _line=None):
        """
        Used to visit a single input line.
        :param _line: a single input line.
        :type _line: ASTInputLine
        """
        return

    def visit_input_type(self, _type=None):
        """
        Used to visit a single input type.
        :param _type: a single input-type.
        :type _type: ASTInputType
        """
        return

    def visit_arithmetic_operator(self, _arithmetic_op=None):
        """
        Used to visit a single arithmetic operator.
        :param _arithmetic_op: a single arithmetic operator.
        :type _arithmetic_op: ASTArithmeticOperator
        """
        return

    def visit_parameter(self, _parameter=None):
        """
        Used to visit a single parameter.
        :param _parameter: a single parameter.
        :type _parameter: ASTParameter
        """
        return

    def end_visit_compilation_unit(self, _compilation_unit=None):
        """
        Visits a single compilation unit, thus all neurons.
        :param _compilation_unit: a single compilation unit.
        :type _compilation_unit: ASTNESTMLCompilationUnit
        """
        return

    def end_visit_neuron(self, _neuron=None):
        """
        Used to endvisit a single neuron.
        :return: a single neuron.
        :rtype: ASTNeuron
        """
        return

    def end_visit_body(self, _body=None):
        """
        Used to endvisit a single neuron body.
        :param _body: a single body element.
        :type _body: ASTBody
        """
        return

    def end_visit_function(self, _block=None):
        """
        Used to endvisit a single function block.
        :param _block: a function block object.
        :type _block: ASTFunction
        """
        return

    def end_visit_update_block(self, _block=None):
        """
        Used to endvisit a single update block.
        :param _block: an update block object. 
        :type _block: ASTDynamics
        """
        return

    def end_visit_block(self, _block=None):
        """
        Used to endvisit a single block of statements.
        :param _block: a block object.
        :type _block: ASTBlock
        """
        return

    def end_visit_small_stmt(self, _stmt=None):
        """
        Used to endvisit a single small statement.
        :param _stmt: a single small statement.
        :type _stmt: ASTSmallStatement
        """
        return

    def end_visit_compound_stmt(self, _stmt=None):
        """
        Used to endvisit a single compound statement.
        :param _stmt: a single compound statement.
        :type _stmt: ASTCompoundStatement
        """
        return

    def end_visit_assignment(self, _assignment=None):
        """
        Used to endvisit a single assignment.
        :param _assignment: an assignment object.
        :type _assignment: ASTAssignment
        """
        return

    def end_visit_function_call(self, _function_call=None):
        """
        Private method: Used to endvisit a single function call and update its corresponding scope.
        :param _function_call: a function call object.
        :type _function_call: ASTFunctionCall
        """
        return

    def end_visit_declaration(self, _declaration=None):
        """
        Used to endvisit a single declaration.
        :param _declaration: a declaration object.
        :type _declaration: ASTDeclaration
        """
        return

    def end_visit_return_stmt(self, _return_stmt=None):
        """
        Used to endvisit a single return statement.
        :param _return_stmt: a return statement object.
        :type _return_stmt: ASTReturnStmt
        """
        return

    def end_visit_if_stmt(self, _if_stmt=None):
        """
        Used to endvisit a single if-statement.
        :param _if_stmt: an if-statement object.
        :type _if_stmt: ASTIfStmt
        """
        return

    def end_visit_if_clause(self, _if_clause=None):
        """
        Used to endvisit a single if-clause.
        :param _if_clause: an if clause.
        :type _if_clause: ASTIfClause
        """
        return

    def end_visit_elif_clause(self, _elif_clause=None):
        """
        Used to endvisit a single elif-clause.
        :param _elif_clause: an elif clause.
        :type _elif_clause: ASTElifClause
        """
        return

    def end_visit_else_clause(self, _else_clause=None):
        """
        Used to endvisit a single else-clause.
        :param _else_clause: an else clause.
        :type _else_clause: ASTElseClause
        """
        return

    def end_visit_for_stmt(self, _for_stmt=None):
        """
        Private method: Used to endvisit a single for-stmt.
        :param _for_stmt: a for-statement.
        :type _for_stmt: ASTForStmt
        """
        return

    def end_visit_while_stmt(self, _while_stmt=None):
        """
        Used to endvisit a single while-stmt.
        :param _while_stmt: a while-statement.
        :type _while_stmt: ASTWhileStmt
        """
        return

    def end_visit_datatype(self, _data_type=None):
        """
        Used to endvisit a single data-type. 
        :param _data_type: a data-type.
        :type _data_type: ASTDataType
        """
        return

    def end_visit_unit_type(self, _unit_type=None):
        """
        Used to endvisit a single unit-type.
        :param _unit_type: a unit type.
        :type _unit_type: ASTUnitType
        """
        return

    def end_visit_expression(self, _expr=None):
        """
        Used to endvisit a single expression.
        :param _expr: an expression.
        :type _expr: ASTExpression
        """
        return

    def end_visit_simple_expression(self, _expr=None):
        """
        Used to endvisit a single simple expression.
        :param _expr: a simple expression. 
        :type _expr: ASTSimpleExpression
        """
        return

    def end_visit_unary_operator(self, _unary_op=None):
        """
        Used to endvisit a single unary operator.
        :param _unary_op: a single unary operator.
        :type _unary_op: ASTUnaryOperator
        """
        return

    def end_visit_bit_operator(self, _bit_op=None):
        """
        Used to endvisit a single unary operator.
        :param _bit_op: a single bit operator.
        :type _bit_op: ASTBitOperator
        """
        return

    def end_visit_comparison_operator(self, _comparison_op=None):
        """
        Used to endvisit a single comparison operator.
        :param _comparison_op: a single comparison operator.
        :type _comparison_op: ASTComparisonOperator
        """
        return

    def end_visit_logical_operator(self, _logical_op=None):
        """
        Used to endvisit a single logical operator.
        :param _logical_op: a single logical operator.
        :type _logical_op: ASTLogicalOperator
        """
        return

    def end_visit_variable(self, _variable=None):
        """
        Used to endvisit a single variable.
        :param _variable: a single variable.
        :type _variable: ASTVariable
        """
        return

    def end_visit_ode_function(self, _ode_function=None):
        """
        Used to endvisit a single ode-function.
        :param _ode_function: a single ode-function.
        :type _ode_function: ASTOdeFunction
        """
        return

    def end_visit_ode_shape(self, _ode_shape=None):
        """
        Used to endvisit a single ode-shape.
        :param _ode_shape: a single ode-shape.
        :type _ode_shape: ASTOdeShape
        """
        return

    def end_visit_ode_equation(self, _equation=None):
        """
        Used to endvisit a single ode-equation.
        :param _equation: a single ode-equation.
        :type _equation: ASTOdeEquation
        """
        return

    def end_visit_block_with_variables(self, _block=None):
        """
        Used to endvisit a single block of variables.
        :param _block: a block with declared variables.
        :type _block: ASTBlockWithVariables
        """
        return

    def end_visit_equations_block(self, _block=None):
        """
        Used to endvisit a single equations block.
        :param _block: a single equations block.
        :type _block: ASTEquationsBlock
        """
        return

    def end_visit_input_block(self, _block=None):
        """
        Used to endvisit a single input block.
        :param _block: a single input block.
        :type _block: ASTInputBlock
        """
        return

    def end_visit_output_block(self, _block=None):
        """
        Used to endvisit a single output block.
        :param _block: a single output block. 
        :type _block: ASTOutputBlock
        """
        return

    def end_visit_input_line(self, _line=None):
        """
        Used to endvisit a single input line.
        :param _line: a single input line.
        :type _line: ASTInputLine
        """
        return

    def end_visit_input_type(self, _type=None):
        """
        Used to endvisit a single input type.
        :param _type: a single input-type.
        :type _type: ASTInputType
        """
        return

    def end_visit_arithmetic_operator(self, _arithmetic_op=None):
        """
        Used to endvisit a single arithmetic operator.
        :param _arithmetic_op: a single arithmetic operator.
        :type _arithmetic_op: ASTArithmeticOperator
        """
        return

    def end_visit_parameter(self, _parameter=None):
        """
        Used to endvisit a single parameter.
        :param _parameter: a single parameter.
        :type _parameter: ASTParameter
        """
        return

    def set_real_self(self, _visitor):
        assert (_visitor is not None and isinstance(_visitor, NESTMLVisitor))
        self.__realSelf = _visitor
        return

    def get_real_self(self):
        return self.__realSelf

    def handle(self, _node):
        self.get_real_self().visit(_node)
        self.get_real_self().traverse(_node)
        self.get_real_self().endvisit(_node)
        return

    def visit(self, _node):
        """
        Dispatcher for visitor pattern.
        :param _node: The ASTElement to visit
        :type _node:  ASTElement or inherited
        """
        if isinstance(_node, ASTArithmeticOperator):
            self.visit_arithmetic_operator(_node)
            return
        if isinstance(_node, ASTAssignment):
            self.visit_assignment(_node)
            return
        if isinstance(_node, ASTBitOperator):
            self.visit_bit_operator(_node)
            return
        if isinstance(_node, ASTBlock):
            self.visit_block(_node)
            return
        if isinstance(_node, ASTBlockWithVariables):
            self.visit_block_with_variables(_node)
            return
        if isinstance(_node, ASTBody):
            self.visit_body(_node)
            return
        if isinstance(_node, ASTComparisonOperator):
            self.visit_comparison_operator(_node)
            return
        if isinstance(_node, ASTCompoundStmt):
            self.visit_compound_stmt(_node)
            return
        if isinstance(_node, ASTDatatype):
            self.visit_datatype(_node)
            return
        if isinstance(_node, ASTDeclaration):
            self.visit_declaration(_node)
            return
        if isinstance(_node, ASTElifClause):
            self.visit_elif_clause(_node)
            return
        if isinstance(_node, ASTElseClause):
            self.visit_else_clause(_node)
            return
        if isinstance(_node, ASTEquationsBlock):
            self.visit_equations_block(_node)
            return
        if isinstance(_node, ASTExpression):
            self.visit_expression(_node)
            return
        if isinstance(_node, ASTForStmt):
            self.visit_for_stmt(_node)
            return
        if isinstance(_node, ASTFunction):
            self.visit_function(_node)
            return
        if isinstance(_node, ASTFunctionCall):
            self.visit_function_call(_node)
            return
        if isinstance(_node, ASTIfClause):
            self.visit_if_clause(_node)
            return
        if isinstance(_node, ASTIfStmt):
            self.visit_if_stmt(_node)
            return
        if isinstance(_node, ASTInputBlock):
            self.visit_input_block(_node)
            return
        if isinstance(_node, ASTInputLine):
            self.visit_input_line(_node)
            return
        if isinstance(_node, ASTInputType):
            self.visit_input_type(_node)
            return
        if isinstance(_node, ASTLogicalOperator):
            self.visit_logical_operator(_node)
            return
        if isinstance(_node, ASTNESTMLCompilationUnit):
            self.visit_compilation_unit(_node)
            return
        if isinstance(_node, ASTNeuron):
            self.visit_neuron(_node)
            return
        if isinstance(_node, ASTOdeEquation):
            self.visit_ode_equation(_node)
            return
        if isinstance(_node, ASTOdeFunction):
            self.visit_ode_function(_node)
            return
        if isinstance(_node, ASTOdeShape):
            self.visit_ode_shape(_node)
            return
        if isinstance(_node, ASTOutputBlock):
            self.visit_output_block(_node)
            return
        if isinstance(_node, ASTParameter):
            self.visit_parameter(_node)
            return
        if isinstance(_node, ASTReturnStmt):
            self.visit_return_stmt(_node)
            return
        if isinstance(_node, ASTSimpleExpression):
            self.visit_simple_expression(_node)
            return
        if isinstance(_node, ASTSmallStmt):
            self.visit_small_stmt(_node)
            return
        if isinstance(_node, ASTUnaryOperator):
            self.visit_unary_operator(_node)
            return
        if isinstance(_node, ASTUnitType):
            self.visit_unit_type(_node)
            return
        if isinstance(_node, ASTUpdateBlock):
            self.visit_update_block(_node)
            return
        if isinstance(_node, ASTVariable):
            self.visit_variable(_node)
            return
        if isinstance(_node, ASTWhileStmt):
            self.visit_while_stmt(_node)
            return
        return

    def traverse(self, _node):
        """
        Dispatcher for traverse method.
        :param _node: The ASTElement to visit
        :type _node: Inherited from ASTElement
        """
        if isinstance(_node, ASTArithmeticOperator):
            self.traverse_arithmetic_operator(_node)
            return
        if isinstance(_node, ASTAssignment):
            self.traverse_assignment(_node)
            return
        if isinstance(_node, ASTBitOperator):
            self.traverse_bit_operator(_node)
            return
        if isinstance(_node, ASTBlock):
            self.traverse_block(_node)
            return
        if isinstance(_node, ASTBlockWithVariables):
            self.traverse_block_with_variables(_node)
            return
        if isinstance(_node, ASTBody):
            self.traverse_body(_node)
            return
        if isinstance(_node, ASTComparisonOperator):
            self.traverse_comparison_operator(_node)
            return
        if isinstance(_node, ASTCompoundStmt):
            self.traverse_compound_stmt(_node)
            return
        if isinstance(_node, ASTDatatype):
            self.traverse_datatype(_node)
            return
        if isinstance(_node, ASTDeclaration):
            self.traverse_declaration(_node)
            return
        if isinstance(_node, ASTElifClause):
            self.traverse_elif_clause(_node)
            return
        if isinstance(_node, ASTElseClause):
            self.traverse_else_clause(_node)
            return
        if isinstance(_node, ASTEquationsBlock):
            self.traverse_equations_block(_node)
            return
        if isinstance(_node, ASTExpression):
            self.traverse_expression(_node)
            return
        if isinstance(_node, ASTForStmt):
            self.traverse_for_stmt(_node)
            return
        if isinstance(_node, ASTFunction):
            self.traverse_function(_node)
            return
        if isinstance(_node, ASTFunctionCall):
            self.traverse_function_call(_node)
            return
        if isinstance(_node, ASTIfClause):
            self.traverse_if_clause(_node)
            return
        if isinstance(_node, ASTIfStmt):
            self.traverse_if_stmt(_node)
            return
        if isinstance(_node, ASTInputBlock):
            self.traverse_input_block(_node)
            return
        if isinstance(_node, ASTInputLine):
            self.traverse_input_line(_node)
            return
        if isinstance(_node, ASTInputType):
            self.traverse_input_type(_node)
            return
        if isinstance(_node, ASTLogicalOperator):
            self.traverse_logical_operator(_node)
            return
        if isinstance(_node, ASTNESTMLCompilationUnit):
            self.traverse_compilation_unit(_node)
            return
        if isinstance(_node, ASTNeuron):
            self.traverse_neuron(_node)
            return
        if isinstance(_node, ASTOdeEquation):
            self.traverse_ode_equation(_node)
            return
        if isinstance(_node, ASTOdeFunction):
            self.traverse_ode_function(_node)
            return
        if isinstance(_node, ASTOdeShape):
            self.traverse_ode_shape(_node)
            return
        if isinstance(_node, ASTOutputBlock):
            self.traverse_output_block(_node)
            return
        if isinstance(_node, ASTParameter):
            self.traverse_parameter(_node)
            return
        if isinstance(_node, ASTReturnStmt):
            self.traverse_return_stmt(_node)
            return
        if isinstance(_node, ASTSimpleExpression):
            self.traverse_simple_expression(_node)
            return
        if isinstance(_node, ASTSmallStmt):
            self.traverse_small_stmt(_node)
            return
        if isinstance(_node, ASTUnaryOperator):
            self.traverse_unary_operator(_node)
            return
        if isinstance(_node, ASTUnitType):
            self.traverse_unit_type(_node)
            return
        if isinstance(_node, ASTUpdateBlock):
            self.traverse_update_block(_node)
            return
        if isinstance(_node, ASTVariable):
            self.traverse_variable(_node)
            return
        if isinstance(_node, ASTWhileStmt):
            self.traverse_while_stmt(_node)
            return
        return

    def endvisit(self, _node):
        """
        Dispatcher for endvisit.
        :param _node: The ASTElement to endvisit
        :type _node:  ASTElement or inherited
        """
        if isinstance(_node, ASTArithmeticOperator):
            self.end_visit_arithmetic_operator(_node)
            return
        if isinstance(_node, ASTAssignment):
            self.end_visit_assignment(_node)
            return
        if isinstance(_node, ASTBitOperator):
            self.end_visit_bit_operator(_node)
            return
        if isinstance(_node, ASTBlock):
            self.end_visit_block(_node)
            return
        if isinstance(_node, ASTBlockWithVariables):
            self.end_visit_block_with_variables(_node)
            return
        if isinstance(_node, ASTBody):
            self.end_visit_body(_node)
            return
        if isinstance(_node, ASTComparisonOperator):
            self.end_visit_comparison_operator()
            return
        if isinstance(_node, ASTCompoundStmt):
            self.end_visit_compound_stmt(_node)
            return
        if isinstance(_node, ASTDatatype):
            self.end_visit_datatype(_node)
            return
        if isinstance(_node, ASTDeclaration):
            self.end_visit_declaration(_node)
            return
        if isinstance(_node, ASTElifClause):
            self.end_visit_elif_clause(_node)
            return
        if isinstance(_node, ASTElseClause):
            self.end_visit_else_clause(_node)
            return
        if isinstance(_node, ASTEquationsBlock):
            self.end_visit_equations_block(_node)
            return
        if isinstance(_node, ASTExpression):
            self.end_visit_expression(_node)
            return
        if isinstance(_node, ASTForStmt):
            self.end_visit_for_stmt(_node)
            return
        if isinstance(_node, ASTFunction):
            self.end_visit_function(_node)
            return
        if isinstance(_node, ASTFunctionCall):
            self.end_visit_function_call(_node)
            return
        if isinstance(_node, ASTIfClause):
            self.end_visit_if_clause(_node)
            return
        if isinstance(_node, ASTIfStmt):
            self.end_visit_if_stmt(_node)
            return
        if isinstance(_node, ASTInputBlock):
            self.end_visit_input_block(_node)
            return
        if isinstance(_node, ASTInputLine):
            self.end_visit_input_line(_node)
            return
        if isinstance(_node, ASTInputType):
            self.end_visit_input_type(_node)
            return
        if isinstance(_node, ASTLogicalOperator):
            self.end_visit_logical_operator(_node)
            return
        if isinstance(_node, ASTNESTMLCompilationUnit):
            self.end_visit_compilation_unit(_node)
            return
        if isinstance(_node, ASTNeuron):
            self.end_visit_neuron(_node)
            return
        if isinstance(_node, ASTOdeEquation):
            self.end_visit_ode_equation(_node)
            return
        if isinstance(_node, ASTOdeFunction):
            self.end_visit_ode_function(_node)
            return
        if isinstance(_node, ASTOdeShape):
            self.end_visit_ode_shape(_node)
            return
        if isinstance(_node, ASTOutputBlock):
            self.end_visit_output_block(_node)
            return
        if isinstance(_node, ASTParameter):
            self.end_visit_parameter(_node)
            return
        if isinstance(_node, ASTReturnStmt):
            self.end_visit_return_stmt(_node)
            return
        if isinstance(_node, ASTSimpleExpression):
            self.end_visit_simple_expression(_node)
            return
        if isinstance(_node, ASTSmallStmt):
            self.end_visit_small_stmt(_node)
            return
        if isinstance(_node, ASTUnaryOperator):
            self.end_visit_unary_operator(_node)
            return
        if isinstance(_node, ASTUnitType):
            self.end_visit_unit_type(_node)
            return
        if isinstance(_node, ASTUpdateBlock):
            self.end_visit_update_block(_node)
            return
        if isinstance(_node, ASTVariable):
            self.end_visit_variable(_node)
            return
        if isinstance(_node, ASTWhileStmt):
            self.end_visit_while_stmt(_node)
            return
        return

    def traverse_arithmetic_operator(self, _node):
        return

    def traverse_assignment(self, _node):
        if _node.getVariable() is not None:
            _node.getVariable().accept(self.get_real_self())
        if _node.getExpression() is not None:
            _node.getExpression().accept(self.get_real_self())
        return

    def traverse_bit_operator(self, _node):
        return

    def traverse_block(self, _node):
        if _node.getStmts() is not None:
            for subnode in _node.getStmts():
                subnode.accept(self.get_real_self())
        return

    def traverse_block_with_variables(self, _node):
        if _node.getDeclarations() is not None:
            for subnode in _node.getDeclarations():
                subnode.accept(self.get_real_self())
        return

    def traverse_body(self, _node):
        if _node.getBodyElements() is not None:
            for subnode in _node.getBodyElements():
                subnode.accept(self.get_real_self())
        return

    def traverse_comparison_operator(self, _node):
        return

    def traverse_compound_stmt(self, _node):
        if _node.getIfStmt() is not None:
            _node.getIfStmt().accept(self.get_real_self())
        if _node.getWhileStmt() is not None:
            _node.getWhileStmt().accept(self.get_real_self())
        if _node.getForStmt() is not None:
            _node.getForStmt().accept(self.get_real_self())
        return

    def traverse_datatype(self, _node):
        if _node.getUnitType() is not None:
            _node.getUnitType().accept(self.get_real_self())
        return

    def traverse_declaration(self, _node):
        if _node.getVariables() is not None:
            for subnode in _node.getVariables():
                subnode.accept(self.get_real_self())
        if _node.getDataType() is not None:
            _node.getDataType().accept(self.get_real_self())
        if _node.getExpression() is not None:
            _node.getExpression().accept(self.get_real_self())
        if _node.getInvariant() is not None:
            _node.getInvariant().accept(self.get_real_self())
        return

    def traverse_elif_clause(self, _node):
        if _node.getCondition() is not None:
            _node.getCondition().accept(self.get_real_self())
        if _node.getBlock() is not None:
            _node.getBlock().accept(self.get_real_self())
        return

    def traverse_else_clause(self, _node):
        if _node.getBlock() is not None:
            _node.getBlock().accept(self.get_real_self())
        return

    def traverse_equations_block(self, _node):
        if _node.getDeclarations() is not None:
            for subnode in _node.getDeclarations():
                subnode.accept(self.get_real_self())
        return

    def traverse_expression(self, _node):
        if _node.getExpression() is not None:
            _node.getExpression().accept(self.get_real_self())
        if _node.getUnaryOperator() is not None:
            _node.getUnaryOperator().accept(self.get_real_self())
        if _node.getLhs() is not None:
            _node.getLhs().accept(self.get_real_self())
        if _node.getRhs() is not None:
            _node.getRhs().accept(self.get_real_self())
        if _node.getBinaryOperator() is not None:
            _node.getBinaryOperator().accept(self.get_real_self())
        if _node.getCondition() is not None:
            _node.getCondition().accept(self.get_real_self())
        if _node.getIfTrue() is not None:
            _node.getIfTrue().accept(self.get_real_self())
        if _node.getIfNot() is not None:
            _node.getIfNot().accept(self.get_real_self())
        return

    def traverse_for_stmt(self, _node):
        if _node.getFrom() is not None:
            _node.getFrom().accept(self.get_real_self())
        if _node.getTo() is not None:
            _node.getTo().accept(self.get_real_self())
        if _node.getBlock() is not None:
            _node.getBlock().accept(self.get_real_self())
        return

    def traverse_function(self, _node):
        if _node.getParameters() is not None:
            for subnode in _node.getParameters():
                subnode.accept(self.get_real_self())
        if _node.get_return_data_type() is not None:
            _node.get_return_data_type().accept(self.get_real_self())
        if _node.getBlock() is not None:
            _node.getBlock().accept(self.get_real_self())
        return

    def traverse_function_call(self, _node):
        if _node.getArgs() is not None:
            for subnode in _node.getArgs():
                subnode.accept(self.get_real_self())
        return

    def traverse_if_clause(self, _node):
        if _node.getCondition() is not None:
            _node.getCondition().accept(self.get_real_self())
        if _node.getBlock() is not None:
            _node.getBlock().accept(self.get_real_self())
        return

    def traverse_if_stmt(self, _node):
        if _node.getIfClause() is not None:
            _node.getIfClause().accept(self.get_real_self())
        for elifClause in _node.getElifClauses():
            elifClause.accept(self.get_real_self())
        if _node.getElseClause() is not None:
            _node.getElseClause().accept(self.get_real_self())
        return

    def traverse_input_block(self, _node):
        if _node.getInputLines() is not None:
            for subnode in _node.getInputLines():
                subnode.accept(self.get_real_self())
        return

    def traverse_input_line(self, _node):
        if _node.getInputTypes() is not None:
            for subnode in _node.getInputTypes():
                subnode.accept(self.get_real_self())
        return

    def traverse_input_type(self, _node):
        return

    def traverse_logical_operator(self, _node):
        return

    def traverse_compilation_unit(self, _node):
        if _node.getNeuronList() is not None:
            for subnode in _node.getNeuronList():
                subnode.accept(self.get_real_self())
        return

    def traverse_neuron(self, _node):
        if _node.getBody() is not None:
            _node.getBody().accept(self.get_real_self())
        return

    def traverse_ode_equation(self, _node):
        if _node.getLhs() is not None:
            _node.getLhs().accept(self.get_real_self())
        if _node.getRhs() is not None:
            _node.getRhs().accept(self.get_real_self())
        return

    def traverse_ode_function(self, _node):
        if _node.getDataType() is not None:
            _node.getDataType().accept(self.get_real_self())
        if _node.getExpression() is not None:
            _node.getExpression().accept(self.get_real_self())
        return

    def traverse_ode_shape(self, _node):
        if _node.getVariable() is not None:
            _node.getVariable().accept(self.get_real_self())
        if _node.getExpression() is not None:
            _node.getExpression().accept(self.get_real_self())
        return

    def traverse_output_block(self, _node):
        return

    def traverse_parameter(self, _node):
        if _node.getDataType() is not None:
            _node.getDataType().accept(self.get_real_self())
        return

    def traverse_return_stmt(self, _node):
        if _node.getExpression() is not None:
            _node.getExpression().accept(self.get_real_self())
        return

    def traverse_simple_expression(self, _node):
        if _node.getFunctionCall() is not None:
            _node.getFunctionCall().accept(self.get_real_self())
        if _node.getVariable() is not None:
            _node.getVariable().accept(self.get_real_self())
        return

    def traverse_small_stmt(self, _node):
        if _node.getAssignment() is not None:
            _node.getAssignment().accept(self.get_real_self())
        if _node.getFunctionCall() is not None:
            _node.getFunctionCall().accept(self.get_real_self())
        if _node.getDeclaration() is not None:
            _node.getDeclaration().accept(self.get_real_self())
        if _node.getReturnStmt() is not None:
            _node.getReturnStmt().accept(self.get_real_self())
        return

    def traverse_unary_operator(self, _node):
        return

    def traverse_unit_type(self, _node):
        if _node.getBase() is not None:
            _node.getBase().accept(self.get_real_self())
        if _node.getLhs() is not None:
            if isinstance(_node.getLhs(), ASTUnitType):
                _node.getLhs().accept(self.get_real_self())
        if _node.getRhs() is not None:
            _node.getRhs().accept(self.get_real_self())
        if _node.getCompoundUnit() is not None:
            _node.getCompoundUnit().accept(self.get_real_self())
        return

    def traverse_update_block(self, _node):
        if _node.getBlock() is not None:
            _node.getBlock().accept(self.get_real_self())
        return

    def traverse_variable(self, node):
        return

    def traverse_while_stmt(self, _node):
        if _node.getCondition() is not None:
            _node.getCondition().accept(self.get_real_self())
        if _node.getBlock() is not None:
            _node.getBlock().accept(self.get_real_self())
        return
