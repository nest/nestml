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
from pynestml.modelprocessor.ASTDatatype import ASTDatatype


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
    def create_ast_assignment(cls, lhs=None, is_direct_assignment=False, is_compound_sum=False, is_compound_minus=False,
                              is_compound_product=False, is_compound_quotient=False, expression=None,
                              source_position=None):
        # type:(ASTVariable,bool,bool,bool,bool,bool,(ASTExpression|ASTSimpleExpression),ASTSourcePosition) -> ASTAssignment
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
    def create_ast_body(cls, body_elements=list(), source_position=None):
        # type: (list,ASTSourcePosition) -> ASTBody
        return ASTBody(body_elements, source_position)

    @classmethod
    def create_ast_comparison_operator(cls, is_lt=False, is_le=False, is_eq=False, is_ne=False, is_ne2=False,
                                       is_ge=False, is_gt=False, source_position=None):
        # type: (bool,bool,bool,bool,bool,bool,bool,ASTSourcePosition) -> ASTComparisonOperator
        return ASTComparisonOperator(is_lt, is_le, is_eq, is_ne, is_ne2, is_ge, is_gt, source_position)

    @classmethod
    def create_ast_compound_stmt(cls, if_stmt=None, while_stmt=None, for_stmt=None, source_position=None):
        # type: (ASTIfStmt,ASTWhileStmt,ASTForStmt,ASTSourcePosition) -> ASTCompoundStmt
        return ASTCompoundStmt(if_stmt, while_stmt, for_stmt, source_position)

    @classmethod
    def create_ast_data_type(cls, is_integer=False, is_real=False, is_string=False, is_boolean=False,
                             is_void=False, is_unit_type=None, source_position=None):
        # type: (bool,bool,bool,bool,bool,ASTUnitType,ASTSourcePosition) -> ASTDatatype
        return ASTDatatype(is_integer, is_real, is_string, is_boolean, is_void, is_unit_type, source_position)

    @classmethod
    def create_ast_declaration(cls, is_recordable=False, is_function=False, variables=list(), data_type=None,
                           size_parameter=None, expression=None, invariant=None, source_position=None):
        # type: (bool,bool,list,ASTDatatype,str,ASTExpression|ASTSimpleExpression,ASTExpression|ASTSimpleExpression,ASTSourcePosition) -> ASTDeclaration
        return ASTDeclaration(is_recordable, is_function, variables, data_type, size_parameter, expression, invariant,
                              source_position)
