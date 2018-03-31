#
# ASTNodeFactory.py
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
from typing import Union

from pynestml.modelprocessor.ASTSourcePosition import ASTSourcePosition
from pynestml.modelprocessor.ASTArithmeticOperator import ASTArithmeticOperator
from pynestml.modelprocessor.ASTExpression import ASTExpression
from pynestml.modelprocessor.ASTSimpleExpression import ASTSimpleExpression
from pynestml.modelprocessor.ASTVariable import ASTVariable
from pynestml.modelprocessor.ASTAssignment import ASTAssignment
from pynestml.modelprocessor.ASTBitOperator import ASTBitOperator
from pynestml.modelprocessor.ASTSmallStmt import ASTSmallStmt
from pynestml.modelprocessor.ASTCompoundStmt import ASTCompoundStmt
from pynestml.modelprocessor.ASTBlock import ASTBlock
from pynestml.modelprocessor.ASTDeclaration import ASTDeclaration
from pynestml.modelprocessor.ASTBlockWithVariables import ASTBlockWithVariables
from pynestml.modelprocessor.ASTBody import ASTBody
from pynestml.modelprocessor.ASTComparisonOperator import ASTComparisonOperator
from pynestml.modelprocessor.ASTIfStmt import ASTIfStmt
from pynestml.modelprocessor.ASTWhileStmt import ASTWhileStmt
from pynestml.modelprocessor.ASTForStmt import ASTForStmt
from pynestml.modelprocessor.ASTUnitType import ASTUnitType
from pynestml.modelprocessor.ASTDataType import ASTDataType
from pynestml.modelprocessor.ASTElifClause import ASTElifClause
from pynestml.modelprocessor.ASTElseClause import ASTElseClause
from pynestml.modelprocessor.ASTEquationsBlock import ASTEquationsBlock
from pynestml.modelprocessor.ASTUnaryOperator import ASTUnaryOperator
from pynestml.modelprocessor.ASTLogicalOperator import ASTLogicalOperator
from pynestml.modelprocessor.ASTParameter import ASTParameter
from pynestml.modelprocessor.ASTFunction import ASTFunction
from pynestml.modelprocessor.ASTFunctionCall import ASTFunctionCall
from pynestml.modelprocessor.ASTIfClause import ASTIfClause
from pynestml.modelprocessor.ASTInputBlock import ASTInputBlock
from pynestml.modelprocessor.ASTInputLine import ASTInputLine
from pynestml.modelprocessor.ASTInputType import ASTInputType
from pynestml.modelprocessor.ASTSignalType import ASTSignalType
from pynestml.modelprocessor.ASTNeuron import ASTNeuron
from pynestml.modelprocessor.ASTNestMLCompilationUnit import ASTNestMLCompilationUnit
from pynestml.modelprocessor.ASTOdeEquation import ASTOdeEquation
from pynestml.modelprocessor.ASTOdeFunction import ASTOdeFunction
from pynestml.modelprocessor.ASTOdeShape import ASTOdeShape
from pynestml.modelprocessor.ASTOutputBlock import ASTOutputBlock
from pynestml.modelprocessor.ASTReturnStmt import ASTReturnStmt
from pynestml.modelprocessor.ASTUpdateBlock import ASTUpdateBlock
from pynestml.modelprocessor.ASTStmt import ASTStmt


class ASTNodeFactory(object):
    """
    An implementation of the factory pattern for an easier initialization of new AST nodes.
    """

    @classmethod
    def create_ast_arithmetic_operator(cls, is_times_op=False, is_div_op=False, is_modulo_op=False, is_plus_op=False,
                                       is_minus_op=False, is_pow_op=False, source_position=None):
        # type:(bool,bool,bool,bool,bool,bool,ASTSourcePosition) -> ASTArithmeticOperator
        return ASTArithmeticOperator(is_times_op, is_div_op, is_modulo_op, is_plus_op, is_minus_op, is_pow_op,
                                     source_position)

    @classmethod
    def create_ast_assignment(cls, lhs=None,  # type: ASTVariable
                              is_direct_assignment=False,  # type: bool
                              is_compound_sum=False,  # type: bool
                              is_compound_minus=False,  # type: bool
                              is_compound_product=False,  # type: bool
                              is_compound_quotient=False,  # type: bool
                              expression=None,  # type: Union(ASTSimpleExpression,ASTExpression)
                              source_position=None  # type: ASTSourcePosition
                              ):  # type: (...) -> ASTAssignment
        return ASTAssignment(lhs, is_direct_assignment, is_compound_sum, is_compound_minus, is_compound_product,
                             is_compound_quotient, expression, source_position)

    @classmethod
    def create_ast_bit_operator(cls, is_bit_and=False, is_bit_xor=False, is_bit_or=False, is_bit_shift_left=False,
                                is_bit_shift_right=False, source_position=None):
        # type: (bool,bool,bool,bool,bool,ASTSourcePosition) -> ASTBitOperator
        return ASTBitOperator(is_bit_and, is_bit_xor, is_bit_or, is_bit_shift_left, is_bit_shift_right, source_position)

    @classmethod
    def create_ast_block(cls, stmts, source_position):
        # type: (list(ASTSmallStmt|ASTCompoundStmt),ASTSourcePosition) -> ASTBlock
        return ASTBlock(stmts, source_position)

    @classmethod
    def create_ast_block_with_variables(cls, is_state=False, is_parameters=False, is_internals=False,
                                        is_initial_values=False, declarations=list(), source_position=None):
        # type: (bool,bool,bool,bool,list(ASTDeclaration),ASTSourcePosition) -> ASTBlockWithVariables
        return ASTBlockWithVariables(is_state, is_parameters, is_internals, is_initial_values, declarations,
                                     source_position)

    @classmethod
    def create_ast_body(cls, body_elements, source_position):
        # type: (list,ASTSourcePosition) -> ASTBody
        return ASTBody(body_elements, source_position)

    @classmethod
    def create_ast_comparison_operator(cls, is_lt=False, is_le=False, is_eq=False, is_ne=False, is_ne2=False,
                                       is_ge=False, is_gt=False, source_position=None):
        # type: (bool,bool,bool,bool,bool,bool,bool,ASTSourcePosition) -> ASTComparisonOperator
        return ASTComparisonOperator(is_lt, is_le, is_eq, is_ne, is_ne2, is_ge, is_gt, source_position)

    @classmethod
    def create_ast_compound_stmt(cls, if_stmt, while_stmt, for_stmt, source_position):
        # type: (ASTIfStmt,ASTWhileStmt,ASTForStmt,ASTSourcePosition) -> ASTCompoundStmt
        return ASTCompoundStmt(if_stmt, while_stmt, for_stmt, source_position)

    @classmethod
    def create_ast_data_type(cls, is_integer=False, is_real=False, is_string=False, is_boolean=False,
                             is_void=False, is_unit_type=None, source_position=None):
        # type: (bool,bool,bool,bool,bool,ASTUnitType,ASTSourcePosition) -> ASTDataType
        return ASTDataType(is_integer, is_real, is_string, is_boolean, is_void, is_unit_type, source_position)

    @classmethod
    def create_ast_declaration(cls,
                               is_recordable=False,  # type: bool
                               is_function=False,  # type: bool
                               variables=list(),  # type: list
                               data_type=None,  # type: ASTDataType
                               size_parameter=None,  # type: str
                               expression=None,  # type: Union(ASTSimpleExpression,ASTExpression)
                               invariant=None,  # type: Union(ASTSimpleExpression,ASTExpression)
                               source_position=None  # type: ASTSourcePosition
                               ):  # type: (...) -> ASTDeclaration
        return ASTDeclaration(is_recordable, is_function, variables, data_type, size_parameter, expression, invariant,
                              source_position)

    @classmethod
    def create_ast_elif_clause(cls, condition, block, source_position=None):
        # type: (ASTExpression|ASTSimpleExpression,ASTBlock,ASTSourcePosition) -> ASTElifClause
        return ASTElifClause(condition, block, source_position)

    @classmethod
    def create_ast_else_clause(cls, block, source_position):
        # type: (ASTBlock,ASTSourcePosition) -> ASTElseClause
        return ASTElseClause(block, source_position)

    @classmethod
    def create_ast_equations_block(cls, declarations=None, source_position=None):
        # type: (ASTBlock,ASTSourcePosition) -> ASTEquationsBlock
        return ASTEquationsBlock(declarations, source_position)

    @classmethod
    def create_ast_expression(cls, is_encapsulated=False, unary_operator=None,
                              is_logical_not=False, expression=None, source_position=None):
        # type: (bool,ASTUnaryOperator,bool,ASTExpression|ASTSimpleExpression,ASTSourcePosition) -> ASTExpression
        """
        The factory method used to create expression which are either encapsulated in parentheses (e.g., (10mV))
        OR have a unary (e.g., ~bitVar), OR are negated (e.g., not logVar), or are simple expression (e.g., 10mV).
        """
        return ASTExpression(is_encapsulated=is_encapsulated, unary_operator=unary_operator,
                             is_logical_not=is_logical_not, expression=expression, source_position=source_position)

    @classmethod
    def create_ast_compound_expression(cls,
                                       lhs,  # type: Union(ASTExpression,ASTSimpleExpression)
                                       binary_operator,
                                       # type: Union(ASTLogicalOperator,ASTBitOperator,ASTComparisonOperator,ASTArithmeticOperator)
                                       rhs,  # type: Union(ASTExpression,ASTSimpleExpression)
                                       source_position  # type: ASTSourcePosition
                                       ):  # type: (...) -> ASTExpression
        """
        The factory method used to create compound expressions, e.g. 10mV + V_m.
        """
        assert (binary_operator is not None and (isinstance(binary_operator, ASTBitOperator) or
                                                 isinstance(binary_operator, ASTComparisonOperator) or
                                                 isinstance(binary_operator, ASTLogicalOperator) or
                                                 isinstance(binary_operator, ASTArithmeticOperator))), \
            '(PyNestML.AST.Expression) No or wrong type of binary operator provided (%s)!' % type(binary_operator)
        return ASTExpression(lhs=lhs, binary_operator=binary_operator, rhs=rhs, source_position=source_position)

    @classmethod
    def create_ast_ternary_expression(cls,
                                      condition,  # type: Union(ASTSimpleExpression,ASTExpression)
                                      if_true,  # type: Union(ASTSimpleExpression,ASTExpression)
                                      if_not,  # type: Union(ASTSimpleExpression,ASTExpression)
                                      source_position  # type: ASTSourcePosition
                                      ):  # type: (...) -> ASTExpression
        """
        The factory method used to create a ternary operator expression, e.g., 10mV<V_m?10mV:V_m
        """
        return ASTExpression(condition=condition, if_true=if_true, if_not=if_not, source_position=source_position)

    @classmethod
    def create_ast_for_stmt(cls,
                            variable,  # type: str
                            start_from,  # type: Union(ASTSimpleExpression,ASTExpression)
                            end_at,  # type: Union(ASTSimpleExpression,ASTExpression)
                            step=0,  # type: float
                            block=None,  # type: ASTBlock
                            source_position=None  # type: ASTSourcePosition
                            ):  # type: (...) -> ASTForStmt
        return ASTForStmt(variable, start_from, end_at, step, block, source_position)

    @classmethod
    def create_ast_function(cls, name, parameters, return_type, block, source_position):
        # type: (str,(None|list(ASTParameter)),(ASTDataType|None),ASTBlock,ASTSourcePosition) -> ASTFunction
        return ASTFunction(name, parameters, return_type, block, source_position)

    @classmethod
    def create_ast_function_call(cls, callee_name, args, source_position):
        # type: (str,(None|list(ASTExpression|ASTSimpleExpression)),ASTSourcePosition) -> ASTFunctionCall
        return ASTFunctionCall(callee_name, args, source_position)

    @classmethod
    def create_ast_if_clause(cls, condition, block, source_position):
        # type: (ASTSimpleExpression|ASTExpression,ASTBlock,ASTSourcePosition) -> ASTIfClause
        return ASTIfClause(condition, block, source_position)

    @classmethod
    def create_ast_if_stmt(cls, if_clause, elif_clauses, else_clause, source_position):
        # type: (ASTIfClause,(None|list(ASTElifClause)),(None|ASTElseClause),ASTSourcePosition) -> ASTIfStmt
        return ASTIfStmt(if_clause, elif_clauses, else_clause, source_position)

    @classmethod
    def create_ast_input_block(cls, input_definitions, source_position):
        # type: (list(ASTInputLine), ASTSourcePosition) -> ASTInputBlock
        return ASTInputBlock(input_definitions, source_position)

    @classmethod
    def create_ast_input_line(cls, name, size_parameter, data_type, input_types, signal_type, source_position):
        # type:(str,str,(None|ASTDataType),list(ASTInputType),ASTSignalType,ASTSourcePosition) -> ASTInputLine
        return ASTInputLine(name=name, size_parameter=size_parameter, data_type=data_type, input_types=input_types,
                            signal_type=signal_type, source_position=source_position)

    @classmethod
    def create_ast_input_type(cls, is_inhibitory=False, is_excitatory=False, source_position=None):
        # type: (bool,bool,ASTSourcePosition) -> ASTInputType
        return ASTInputType(is_inhibitory, is_excitatory, source_position)

    @classmethod
    def create_ast_logical_operator(cls, is_logical_and=False, is_logical_or=False, source_position=None):
        # type: (bool,bool,ASTSourcePosition) -> ASTLogicalOperator
        return ASTLogicalOperator(is_logical_and, is_logical_or, source_position)

    @classmethod
    def create_ast_nestml_compilation_unit(cls, list_of_neurons, source_position, artifact_name):
        # type: (list(ASTNeuron),ASTSourcePosition,str) -> ASTNestMLCompilationUnit
        instance = ASTNestMLCompilationUnit(source_position, artifact_name)
        for i in list_of_neurons:
            instance.addNeuron(i)
        return instance

    @classmethod
    def create_ast_neuron(cls, name, body, source_position, artifact_name):
        # type: (str,ASTBody,ASTSourcePosition,str) -> ASTNeuron
        return ASTNeuron(name, body, source_position, artifact_name)

    @classmethod
    def create_ast_ode_equation(cls, lhs, rhs, source_position):
        # type: (ASTVariable,ASTSimpleExpression|ASTExpression,ASTSourcePosition) -> ASTOdeEquation
        return ASTOdeEquation(lhs, rhs, source_position)

    @classmethod
    def create_ast_ode_function(cls, variable_name, data_type, expression, source_position, is_recordable=False):
        # type: (str,ASTDataType,ASTExpression|ASTSimpleExpression,ASTSourcePosition,bool) -> ASTOdeFunction
        return ASTOdeFunction(variable_name=variable_name, data_type=data_type, expression=expression,
                              source_position=source_position, is_recordable=is_recordable, )

    @classmethod
    def create_ast_ode_shape(cls, lhs=None, rhs=None, source_position=None):
        # type: (ASTVariable,ASTSimpleExpression|ASTExpression,ASTSourcePosition) -> ASTOdeShape
        return ASTOdeShape(lhs, rhs, source_position)

    @classmethod
    def create_ast_output_block(cls, s_type, source_position):
        # type: (ASTSignalType,ASTSourcePosition) -> ASTOutputBlock
        return ASTOutputBlock(s_type, source_position)

    @classmethod
    def create_ast_parameter(cls, name, data_type, source_position):
        # type: (str,ASTDataType,ASTSourcePosition) -> ASTParameter
        return ASTParameter(name=name, data_type=data_type, source_position=source_position)

    @classmethod
    def create_ast_return_stmt(cls, expression=None, source_position=None):
        # type: (ASTSimpleExpression|ASTExpression,ASTSourcePosition) -> ASTReturnStmt
        return ASTReturnStmt(expression, source_position)

    @classmethod
    def create_ast_simple_expression(cls, function_call=None,  # type: ASTFunctionCall
                                     boolean_literal=None,  # type: bool
                                     numeric_literal=None,  # type: Union(float,int)
                                     is_inf=False,  # type: bool
                                     variable=None,  # type: ASTVariable
                                     string=None,  # type: str
                                     source_position=None  # type: ASTSourcePosition
                                     ):  # type: (...) -> ASTSimpleExpression
        return ASTSimpleExpression(function_call, boolean_literal, numeric_literal, is_inf, variable, string,
                                   source_position)

    @classmethod
    def create_ast_small_stmt(cls,
                              assignment=None,  # type: ASTAssignment
                              function_call=None,  # type: ASTFunctionCall
                              declaration=None,  # type: ASTDeclaration
                              return_stmt=None,  # type: ASTReturnStmt
                              source_position=None  # type: ASTSourcePosition
                              ):  # type: (...) -> ASTSmallStmt
        return ASTSmallStmt(assignment, function_call, declaration, return_stmt, source_position)

    @classmethod
    def create_ast_unary_operator(cls, is_unary_plus=False, is_unary_minus=False, is_unary_tilde=False,
                                  source_position=None):
        # type: (bool,bool,bool,ASTSourcePosition) -> ASTUnaryOperator
        return ASTUnaryOperator(is_unary_plus, is_unary_minus, is_unary_tilde, source_position)

    @classmethod
    def create_ast_unit_type(cls,
                             left_parentheses=False,  # type: bool
                             compound_unit=None,  # type: ASTUnitType
                             right_parentheses=False,  # type: bool
                             base=None,  # type: ASTUnitType
                             is_pow=False,  # type: bool
                             exponent=None,  # type: int
                             lhs=None,  # type: Union(ASTUnitType,int)
                             rhs=None,  # type: ASTUnitType
                             is_div=False,  # type: bool
                             is_times=False,  # type: bool
                             unit=None,  # type: str
                             source_position=None  # type: ASTSourcePosition
                             ):  # type: (...) -> ASTUnitType
        return ASTUnitType(left_parentheses, compound_unit, right_parentheses, base, is_pow, exponent, lhs, rhs, is_div,
                           is_times, unit, source_position)

    @classmethod
    def create_ast_update_block(cls, block, source_position):
        # type: (ASTBlock,ASTSourcePosition) -> ASTUpdateBlock
        return ASTUpdateBlock(block, source_position)

    @classmethod
    def create_ast_variable(cls, name, differential_order=0, source_position=None):
        # type: (str,int,ASTSourcePosition) -> ASTVariable
        return ASTVariable(name, differential_order, source_position)

    @classmethod
    def create_ast_while_stmt(cls,
                              condition,  # type: Union(ASTSimpleExpression,ASTExpression)
                              block,  # type: ASTBlock
                              source_position  # type: ASTSourcePosition
                              ):  # type: (...) -> ASTWhileStmt
        return ASTWhileStmt(condition, block, source_position)

    @classmethod
    def create_ast_stmt(cls, small_stmt=None, compound_stmt=None, source_position=None):
        # type: (ASTSmallStmt,ASTCompoundStmt,ASTSourcePosition) -> ASTStmt
        return ASTStmt(small_stmt, compound_stmt, source_position)
