# -*- coding: utf-8 -*-
#
# ast_node_factory.py
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

from pynestml.utils.ast_source_location import ASTSourceLocation
from pynestml.meta_model.ast_arithmetic_operator import ASTArithmeticOperator
from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.meta_model.ast_assignment import ASTAssignment
from pynestml.meta_model.ast_bit_operator import ASTBitOperator
from pynestml.meta_model.ast_small_stmt import ASTSmallStmt
from pynestml.meta_model.ast_compound_stmt import ASTCompoundStmt
from pynestml.meta_model.ast_block import ASTBlock
from pynestml.meta_model.ast_declaration import ASTDeclaration
from pynestml.meta_model.ast_block_with_variables import ASTBlockWithVariables
from pynestml.meta_model.ast_body import ASTBody
from pynestml.meta_model.ast_comparison_operator import ASTComparisonOperator
from pynestml.meta_model.ast_if_stmt import ASTIfStmt
from pynestml.meta_model.ast_while_stmt import ASTWhileStmt
from pynestml.meta_model.ast_for_stmt import ASTForStmt
from pynestml.meta_model.ast_unit_type import ASTUnitType
from pynestml.meta_model.ast_data_type import ASTDataType
from pynestml.meta_model.ast_elif_clause import ASTElifClause
from pynestml.meta_model.ast_else_clause import ASTElseClause
from pynestml.meta_model.ast_equations_block import ASTEquationsBlock
from pynestml.meta_model.ast_unary_operator import ASTUnaryOperator
from pynestml.meta_model.ast_logical_operator import ASTLogicalOperator
from pynestml.meta_model.ast_parameter import ASTParameter
from pynestml.meta_model.ast_function import ASTFunction
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.meta_model.ast_if_clause import ASTIfClause
from pynestml.meta_model.ast_input_block import ASTInputBlock
from pynestml.meta_model.ast_input_port import ASTInputPort
from pynestml.meta_model.ast_input_qualifier import ASTInputQualifier
from pynestml.meta_model.ast_neuron import ASTNeuron
from pynestml.meta_model.ast_nestml_compilation_unit import ASTNestMLCompilationUnit
from pynestml.meta_model.ast_ode_equation import ASTOdeEquation
from pynestml.meta_model.ast_inline_expression import ASTInlineExpression
from pynestml.meta_model.ast_kernel import ASTKernel
from pynestml.meta_model.ast_output_block import ASTOutputBlock
from pynestml.meta_model.ast_return_stmt import ASTReturnStmt
from pynestml.meta_model.ast_update_block import ASTUpdateBlock
from pynestml.meta_model.ast_stmt import ASTStmt
from pynestml.utils.port_signal_type import PortSignalType


class ASTNodeFactory():
    """
    An implementation of the factory pattern for an easier initialization of new AST nodes.
    """

    @classmethod
    def create_ast_arithmetic_operator(cls, is_times_op=False, is_div_op=False, is_modulo_op=False, is_plus_op=False,
                                       is_minus_op=False, is_pow_op=False, source_position=None):
        # type:(bool,bool,bool,bool,bool,bool,ASTSourceLocation) -> ASTArithmeticOperator
        return ASTArithmeticOperator(is_times_op, is_div_op, is_modulo_op, is_plus_op, is_minus_op, is_pow_op,
                                     source_position=source_position)

    @classmethod
    def create_ast_assignment(cls, lhs=None,  # type: ASTVariable
                              is_direct_assignment=False,  # type: bool
                              is_compound_sum=False,  # type: bool
                              is_compound_minus=False,  # type: bool
                              is_compound_product=False,  # type: bool
                              is_compound_quotient=False,  # type: bool
                              expression=None,  # type: Union(ASTSimpleExpression,ASTExpression)
                              source_position=None  # type: ASTSourceLocation
                              ):  # type: (...) -> ASTAssignment
        return ASTAssignment(lhs, is_direct_assignment, is_compound_sum, is_compound_minus, is_compound_product,
                             is_compound_quotient, expression, source_position=source_position)

    @classmethod
    def create_ast_bit_operator(cls, is_bit_and=False, is_bit_xor=False, is_bit_or=False, is_bit_shift_left=False,
                                is_bit_shift_right=False, source_position=None):
        # type: (bool,bool,bool,bool,bool,ASTSourceLocation) -> ASTBitOperator
        return ASTBitOperator(is_bit_and, is_bit_xor, is_bit_or, is_bit_shift_left, is_bit_shift_right, source_position=source_position)

    @classmethod
    def create_ast_block(cls, stmts, source_position):
        # type: (list(ASTSmallStmt|ASTCompoundStmt),ASTSourceLocation) -> ASTBlock
        return ASTBlock(stmts, source_position=source_position)

    @classmethod
    def create_ast_block_with_variables(cls, is_state=False, is_parameters=False, is_internals=False,
                                        is_initial_values=False, declarations=None, source_position=None):
        # type: (bool,bool,bool,bool,list(ASTDeclaration),ASTSourceLocation) -> ASTBlockWithVariables
        return ASTBlockWithVariables(is_state, is_parameters, is_internals, is_initial_values, declarations,
                                     source_position=source_position)

    @classmethod
    def create_ast_body(cls, body_elements, source_position):
        # type: (list,ASTSourceLocation) -> ASTBody
        return ASTBody(body_elements, source_position=source_position)

    @classmethod
    def create_ast_comparison_operator(cls, is_lt=False, is_le=False, is_eq=False, is_ne=False, is_ne2=False,
                                       is_ge=False, is_gt=False, source_position=None):
        # type: (bool,bool,bool,bool,bool,bool,bool,ASTSourceLocation) -> ASTComparisonOperator
        return ASTComparisonOperator(is_lt, is_le, is_eq, is_ne, is_ne2, is_ge, is_gt, source_position=source_position)

    @classmethod
    def create_ast_compound_stmt(cls, if_stmt, while_stmt, for_stmt, source_position):
        # type: (ASTIfStmt,ASTWhileStmt,ASTForStmt,ASTSourceLocation) -> ASTCompoundStmt
        return ASTCompoundStmt(if_stmt, while_stmt, for_stmt, source_position=source_position)

    @classmethod
    def create_ast_data_type(cls, is_integer=False, is_real=False, is_string=False, is_boolean=False,
                             is_void=False, is_unit_type=None, source_position=None):
        # type: (bool,bool,bool,bool,bool,ASTUnitType,ASTSourceLocation) -> ASTDataType
        return ASTDataType(is_integer, is_real, is_string, is_boolean, is_void, is_unit_type, source_position=source_position)

    @classmethod
    def create_ast_declaration(cls,
                               is_recordable=False,  # type: bool
                               is_function=False,  # type: bool
                               variables=None,  # type: list
                               data_type=None,  # type: ASTDataType
                               size_parameter=None,  # type: str
                               expression=None,  # type: Union(ASTSimpleExpression,ASTExpression)
                               invariant=None,  # type: Union(ASTSimpleExpression,ASTExpression)
                               source_position=None  # type: ASTSourceLocation
                               ):  # type: (...) -> ASTDeclaration
        return ASTDeclaration(is_recordable, is_function, variables, data_type, size_parameter, expression, invariant,
                              source_position=source_position)

    @classmethod
    def create_ast_elif_clause(cls, condition, block, source_position=None):
        # type: (ASTExpression|ASTSimpleExpression,ASTBlock,ASTSourceLocation) -> ASTElifClause
        return ASTElifClause(condition, block, source_position=source_position)

    @classmethod
    def create_ast_else_clause(cls, block, source_position):
        # type: (ASTBlock,ASTSourceLocation) -> ASTElseClause
        return ASTElseClause(block, source_position=source_position)

    @classmethod
    def create_ast_equations_block(cls, declarations=None, source_position=None):
        # type: (list,ASTSourceLocation) -> ASTEquationsBlock
        return ASTEquationsBlock(declarations, source_position=source_position)

    @classmethod
    def create_ast_expression(cls, is_encapsulated=False, unary_operator=None,
                              is_logical_not=False, expression=None, source_position=None):
        # type: (bool,ASTUnaryOperator,bool,ASTExpression|ASTSimpleExpression,ASTSourceLocation) -> ASTExpression
        """
        The factory method used to create rhs which are either encapsulated in parentheses (e.g., (10mV))
        OR have a unary (e.g., ~bitVar), OR are negated (e.g., not logVar), or are simple rhs (e.g., 10mV).
        """
        return ASTExpression(is_encapsulated=is_encapsulated, unary_operator=unary_operator,
                             is_logical_not=is_logical_not, expression=expression, source_position=source_position)

    @classmethod
    def create_ast_compound_expression(cls,
                                       lhs,  # type: Union(ASTExpression,ASTSimpleExpression)
                                       binary_operator,
                                       # type: Union(ASTLogicalOperator,ASTBitOperator,ASTComparisonOperator,ASTArithmeticOperator)
                                       rhs,  # type: Union(ASTExpression,ASTSimpleExpression)
                                       source_position  # type: ASTSourceLocation
                                       ):  # type: (...) -> ASTExpression
        """
        The factory method used to create compound expressions, e.g. 10mV + V_m.
        """
        assert (binary_operator is not None and (isinstance(binary_operator, ASTBitOperator)
                                                 or isinstance(binary_operator, ASTComparisonOperator)
                                                 or isinstance(binary_operator, ASTLogicalOperator)
                                                 or isinstance(binary_operator, ASTArithmeticOperator))), \
            '(PyNestML.AST.Expression) No or wrong type of binary operator provided (%s)!' % type(binary_operator)
        return ASTExpression(lhs=lhs, binary_operator=binary_operator, rhs=rhs, source_position=source_position)

    @classmethod
    def create_ast_ternary_expression(cls,
                                      condition,  # type: Union(ASTSimpleExpression,ASTExpression)
                                      if_true,  # type: Union(ASTSimpleExpression,ASTExpression)
                                      if_not,  # type: Union(ASTSimpleExpression,ASTExpression)
                                      source_position  # type: ASTSourceLocation
                                      ):  # type: (...) -> ASTExpression
        """
        The factory method used to create a ternary operator rhs, e.g., 10mV<V_m?10mV:V_m
        """
        return ASTExpression(condition=condition, if_true=if_true, if_not=if_not, source_position=source_position)

    @classmethod
    def create_ast_for_stmt(cls,
                            variable,  # type: str
                            start_from,  # type: Union(ASTSimpleExpression,ASTExpression)
                            end_at,  # type: Union(ASTSimpleExpression,ASTExpression)
                            step=0,  # type: float
                            block=None,  # type: ASTBlock
                            source_position=None  # type: ASTSourceLocation
                            ):  # type: (...) -> ASTForStmt
        return ASTForStmt(variable, start_from, end_at, step, block, source_position=source_position)

    @classmethod
    def create_ast_function(cls, name, parameters, return_type, block, source_position):
        # type: (str,(None|list(ASTParameter)),(ASTDataType|None),ASTBlock,ASTSourceLocation) -> ASTFunction
        return ASTFunction(name, parameters, return_type, block, source_position=source_position)

    @classmethod
    def create_ast_function_call(cls, callee_name, args, source_position):
        # type: (str,(None|list(ASTExpression|ASTSimpleExpression)),ASTSourceLocation) -> ASTFunctionCall
        return ASTFunctionCall(callee_name, args, source_position=source_position)

    @classmethod
    def create_ast_if_clause(cls, condition, block, source_position):
        # type: (ASTSimpleExpression|ASTExpression,ASTBlock,ASTSourceLocation) -> ASTIfClause
        return ASTIfClause(condition, block, source_position=source_position)

    @classmethod
    def create_ast_if_stmt(cls, if_clause, elif_clauses, else_clause, source_position):
        # type: (ASTIfClause,(None|list(ASTElifClause)),(None|ASTElseClause),ASTSourceLocation) -> ASTIfStmt
        return ASTIfStmt(if_clause, elif_clauses, else_clause, source_position=source_position)

    @classmethod
    def create_ast_input_block(cls, input_definitions, source_position):
        # type: (list(ASTInputPort), ASTSourceLocation) -> ASTInputBlock
        return ASTInputBlock(input_definitions, source_position=source_position)

    @classmethod
    def create_ast_input_port(cls, name, size_parameter, data_type, input_qualifiers, signal_type, source_position):
        # type:(str,str,(None|ASTDataType),list(ASTInputQualifier),PortSignalType,ASTSourceLocation) -> ASTInputPort
        return ASTInputPort(name=name, size_parameter=size_parameter, data_type=data_type, input_qualifiers=input_qualifiers,
                            signal_type=signal_type, source_position=source_position)

    @classmethod
    def create_ast_input_qualifier(cls, is_inhibitory=False, is_excitatory=False, source_position=None):
        # type: (bool,bool,ASTSourceLocation) -> ASTInputQualifier
        return ASTInputQualifier(is_inhibitory, is_excitatory, source_position=source_position)

    @classmethod
    def create_ast_logical_operator(cls, is_logical_and=False, is_logical_or=False, source_position=None):
        # type: (bool,bool,ASTSourceLocation) -> ASTLogicalOperator
        return ASTLogicalOperator(is_logical_and, is_logical_or, source_position=source_position)

    @classmethod
    def create_ast_nestml_compilation_unit(cls, list_of_neurons, source_position, artifact_name):
        # type: (list(ASTNeuron),ASTSourceLocation,str) -> ASTNestMLCompilationUnit
        return ASTNestMLCompilationUnit(artifact_name=artifact_name, neuron_list=list_of_neurons, source_position=source_position)

    @classmethod
    def create_ast_neuron(cls, name, body, source_position, artifact_name):
        # type: (str,ASTBody,ASTSourceLocation,str) -> ASTNeuron
        return ASTNeuron(name, body, artifact_name, source_position=source_position)

    @classmethod
    def create_ast_ode_equation(cls, lhs, rhs, source_position):
        # type: (ASTVariable,ASTSimpleExpression|ASTExpression,ASTSourceLocation) -> ASTOdeEquation
        return ASTOdeEquation(lhs, rhs, source_position=source_position)

    @classmethod
    def create_ast_inline_expression(cls, variable_name, data_type, expression, source_position, is_recordable=False):
        # type: (str,ASTDataType,ASTExpression|ASTSimpleExpression,ASTSourceLocation,bool) -> ASTInlineExpression
        return ASTInlineExpression(variable_name=variable_name, data_type=data_type, expression=expression,
                                   is_recordable=is_recordable, source_position=source_position)

    @classmethod
    def create_ast_kernel(cls, variables=None, expressions=None, source_position=None):
        # type: (ASTVariable,ASTSimpleExpression|ASTExpression,ASTSourceLocation) -> ASTKernel
        return ASTKernel(variables, expressions, source_position=source_position)

    @classmethod
    def create_ast_output_block(cls, s_type, source_position):
        # type: (PortSignalType,ASTSourceLocation) -> ASTOutputBlock
        return ASTOutputBlock(s_type, source_position=source_position)

    @classmethod
    def create_ast_parameter(cls, name, data_type, source_position):
        # type: (str,ASTDataType,ASTSourceLocation) -> ASTParameter
        return ASTParameter(name=name, data_type=data_type, source_position=source_position)

    @classmethod
    def create_ast_return_stmt(cls, expression=None, source_position=None):
        # type: (ASTSimpleExpression|ASTExpression,ASTSourceLocation) -> ASTReturnStmt
        return ASTReturnStmt(expression, source_position=source_position)

    @classmethod
    def create_ast_simple_expression(cls, function_call=None,  # type: Union(ASTFunctionCall,None)
                                     boolean_literal=None,  # type: Union(bool,None)
                                     numeric_literal=None,  # type: Union(float,int)
                                     is_inf=False,  # type: bool
                                     variable=None,  # type: ASTVariable
                                     string=None,  # type: Union(str,None)
                                     source_position=None  # type: ASTSourceLocation
                                     ):  # type: (...) -> ASTSimpleExpression
        return ASTSimpleExpression(function_call, boolean_literal, numeric_literal, is_inf, variable, string,
                                   source_position=source_position)

    @classmethod
    def create_ast_small_stmt(cls,
                              assignment=None,  # type: ASTAssignment
                              function_call=None,  # type: ASTFunctionCall
                              declaration=None,  # type: ASTDeclaration
                              return_stmt=None,  # type: ASTReturnStmt
                              source_position=None  # type: ASTSourceLocation
                              ):  # type: (...) -> ASTSmallStmt
        return ASTSmallStmt(assignment, function_call, declaration, return_stmt, source_position=source_position)

    @classmethod
    def create_ast_unary_operator(cls, is_unary_plus=False, is_unary_minus=False, is_unary_tilde=False,
                                  source_position=None):
        # type: (bool,bool,bool,ASTSourceLocation) -> ASTUnaryOperator
        return ASTUnaryOperator(is_unary_plus, is_unary_minus, is_unary_tilde, source_position=source_position)

    @classmethod
    def create_ast_unit_type(cls,
                             is_encapsulated=False,  # type: bool
                             compound_unit=None,  # type: ASTUnitType
                             base=None,  # type: ASTUnitType
                             is_pow=False,  # type: bool
                             exponent=None,  # type: int
                             lhs=None,  # type: Union(ASTUnitType,int)
                             rhs=None,  # type: ASTUnitType
                             is_div=False,  # type: bool
                             is_times=False,  # type: bool
                             unit=None,  # type: str
                             source_position=None  # type: ASTSourceLocation
                             ):  # type: (...) -> ASTUnitType
        return ASTUnitType(is_encapsulated, compound_unit, base, is_pow, exponent, lhs, rhs, is_div,
                           is_times, unit, source_position=source_position)

    @classmethod
    def create_ast_update_block(cls, block, source_position):
        # type: (ASTBlock,ASTSourceLocation) -> ASTUpdateBlock
        return ASTUpdateBlock(block, source_position=source_position)

    @classmethod
    def create_ast_variable(cls, name, differential_order=0, source_position=None):
        # type: (str,int,ASTSourceLocation) -> ASTVariable
        return ASTVariable(name, differential_order, source_position=source_position)

    @classmethod
    def create_ast_while_stmt(cls,
                              condition,  # type: Union(ASTSimpleExpression,ASTExpression)
                              block,  # type: ASTBlock
                              source_position  # type: ASTSourceLocation
                              ):  # type: (...) -> ASTWhileStmt
        return ASTWhileStmt(condition, block, source_position=source_position)

    @classmethod
    def create_ast_stmt(cls, small_stmt=None, compound_stmt=None, source_position=None):
        # type: (ASTSmallStmt,ASTCompoundStmt,ASTSourceLocation) -> ASTStmt
        return ASTStmt(small_stmt, compound_stmt, source_position=source_position)
