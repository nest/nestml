# -*- coding: utf-8 -*-
#
# ast_assignment.py
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

from typing import Optional

from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.meta_model.ast_expression import ASTExpression


class ASTAssignment(ASTNode):
    """
    This class is used to store assignments.
    Grammar:
        assignment : lhs_variable=variable
            (directAssignment='='       |
            compoundSum='+='     |
            compoundMinus='-='   |
            compoundProduct='*=' |
            compoundQuotient='/=') rhs;

    Attributes:
        lhs = None
        is_direct_assignment = False
        is_compound_sum = False
        is_compound_minus = False
        is_compound_product = False
        is_compound_quotient = False
        rhs = None
    """

    def __init__(self, lhs: Optional[ASTVariable] = None, is_direct_assignment: bool = False, is_compound_sum: bool = False, is_compound_minus: bool = False,
                 is_compound_product: bool = False, is_compound_quotient: bool = False, rhs: Optional[ASTExpression] = None, *args, **kwargs):
        """
        Standard constructor.

        Parameters for superclass (ASTNode) can be passed through :python:`*args` and :python:`**kwargs`.

        :param lhs: the left-hand side variable to which is assigned to
        :type lhs: Optional[ASTVariable]
        :param is_direct_assignment: is a direct assignment
        :type is_direct_assignment: bool
        :param is_compound_sum: is a compound sum
        :type is_compound_sum: bool
        :param is_compound_minus: is a compound minus
        :type is_compound_minus: bool
        :param is_compound_product: is a compound product
        :type is_compound_product: bool
        :param is_compound_quotient: is a compound quotient
        :type is_compound_quotient: bool
        :param rhs: an meta_model-rhs object
        :type rhs: Optional[ASTExpression]
        """
        super(ASTAssignment, self).__init__(*args, **kwargs)
        self.lhs = lhs
        self.is_direct_assignment = is_direct_assignment
        self.is_compound_sum = is_compound_sum
        self.is_compound_minus = is_compound_minus
        self.is_compound_product = is_compound_product
        self.is_compound_quotient = is_compound_quotient
        self.rhs = rhs

    def clone(self):
        """
        Return a clone ("deep copy") of this node.

        :return: new AST node instance
        :rtype: ASTAssignment
        """
        lhs_dup = None
        if self.lhs:
            lhs_dup = self.lhs.clone()
        rhs_dup = None
        if self.rhs:
            rhs_dup = self.rhs.clone()
        dup = ASTAssignment(lhs=lhs_dup,
                            rhs=rhs_dup,
                            is_direct_assignment=self.is_direct_assignment,
                            is_compound_sum=self.is_compound_sum,
                            is_compound_minus=self.is_compound_minus,
                            is_compound_product=self.is_compound_product,
                            is_compound_quotient=self.is_compound_quotient,
                            # ASTNode common attriutes:
                            source_position=self.source_position,
                            scope=self.scope,
                            comment=self.comment,
                            pre_comments=[s for s in self.pre_comments],
                            in_comment=self.in_comment,
                            post_comments=[s for s in self.post_comments],
                            implicit_conversion_factor=self.implicit_conversion_factor)

        return dup

    def get_variable(self):
        """
        Returns the left-hand side variable.
        :return: left-hand side variable object.
        :rtype: ASTVariable
        """
        return self.lhs

    def get_expression(self):
        """
        Returns the right-hand side rhs.
        :return: rhs object.
        :rtype: ast_expression
        """
        return self.rhs

    def get_parent(self, ast):
        """
        Indicates whether a this node contains the handed over node.
        :param ast: an arbitrary meta_model node.
        :type ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        if self.get_variable() is ast:
            return self
        if self.get_expression() is ast:
            return self
        if self.get_variable().get_parent(ast) is not None:
            return self.get_variable().get_parent(ast)
        if self.get_expression().get_parent(ast) is not None:
            return self.get_expression().get_parent(ast)
        return None

    def equals(self, other):
        """
        The equals operation.
        :param other: a different object.
        :type other: object
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if not isinstance(other, ASTAssignment):
            return False
        return (self.get_variable().equals(other.get_variable())
                and self.is_compound_quotient == other.is_compound_quotient
                and self.is_compound_product == other.is_compound_product
                and self.is_compound_minus == other.is_compound_minus
                and self.is_compound_sum == other.is_compound_sum
                and self.is_direct_assignment == other.is_direct_assignment
                and self.get_expression().equals(other.get_expression()))

    def deconstruct_compound_assignment(self):
        """
        From lhs and rhs it constructs a new expression which corresponds to direct assignment.
        E.g.: a += b*c -> a = a + b*c
        :return: the rhs for an equivalent direct assignment.
        :rtype: ast_expression
        """
        from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor
        # TODO: get rid of this through polymorphism?
        assert not self.is_direct_assignment, "Can only be invoked on a compound assignment."

        operator = self.extract_operator_from_compound_assignment()
        lhs_variable = self.get_lhs_variable_as_expression()
        rhs_in_brackets = self.get_bracketed_rhs_expression()
        result = self.construct_equivalent_direct_assignment_rhs(operator, lhs_variable, rhs_in_brackets)
        # create symbols for the new Expression:
        visitor = ASTSymbolTableVisitor()
        result.accept(visitor)
        return result

    def get_lhs_variable_as_expression(self):
        from pynestml.meta_model.ast_node_factory import ASTNodeFactory
        # TODO: maybe calculate new source positions exactly?
        result = ASTNodeFactory.create_ast_simple_expression(variable=self.get_variable(),
                                                             source_position=self.get_variable().get_source_position())
        result.update_scope(self.get_scope())
        return result

    def extract_operator_from_compound_assignment(self):
        from pynestml.meta_model.ast_node_factory import ASTNodeFactory
        assert not self.is_direct_assignment
        # TODO: maybe calculate new source positions exactly?
        result = None
        if self.is_compound_minus:
            result = ASTNodeFactory.create_ast_arithmetic_operator(is_minus_op=True,
                                                                   source_position=self.get_source_position())
        elif self.is_compound_product:
            result = ASTNodeFactory.create_ast_arithmetic_operator(is_times_op=True,
                                                                   source_position=self.get_source_position())
        elif self.is_compound_quotient:
            result = ASTNodeFactory.create_ast_arithmetic_operator(is_div_op=True,
                                                                   source_position=self.get_source_position())
        elif self.is_compound_sum:
            result = ASTNodeFactory.create_ast_arithmetic_operator(is_plus_op=True,
                                                                   source_position=self.get_source_position())
        else:
            raise RuntimeError('Type of compound operator not recognized!')
        result.update_scope(self.get_scope())
        return result

    def get_bracketed_rhs_expression(self):
        from pynestml.meta_model.ast_node_factory import ASTNodeFactory
        # TODO: maybe calculate new source positions exactly?
        result = ASTNodeFactory.create_ast_expression(is_encapsulated=True,
                                                      expression=self.get_expression(),
                                                      source_position=self.get_expression().get_source_position())
        result.update_scope(self.get_scope())
        return result

    def construct_equivalent_direct_assignment_rhs(self, operator, lhs_variable, rhs_in_brackets):
        from pynestml.meta_model.ast_node_factory import ASTNodeFactory
        # TODO: maybe calculate new source positions exactly?
        result = ASTNodeFactory.create_ast_compound_expression(lhs=lhs_variable, binary_operator=operator,
                                                               rhs=rhs_in_brackets,
                                                               source_position=self.get_source_position())
        result.update_scope(self.get_scope())
        return result
