# -*- coding: utf-8 -*-
#
# ast_expression.py
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

from pynestml.meta_model.ast_expression_node import ASTExpressionNode
from pynestml.meta_model.ast_logical_operator import ASTLogicalOperator
from pynestml.meta_model.ast_arithmetic_operator import ASTArithmeticOperator
from pynestml.meta_model.ast_bit_operator import ASTBitOperator
from pynestml.meta_model.ast_comparison_operator import ASTComparisonOperator


class ASTExpression(ASTExpressionNode):
    """
    ASTExpr, i.e., several subexpressions combined by one or more operators, e.g., 10mV + V_m - (V_reset * 2)/ms ....
    or a simple rhs, e.g. 10mV.
    Grammar:
      rhs : leftParentheses='(' rhs rightParentheses=')'
             | <assoc=right> base=rhs powOp='**' exponent=rhs
             | unaryOperator term=rhs
             | left=rhs (timesOp='*' | divOp='/' | moduloOp='%') right=rhs
             | left=rhs (plusOp='+'  | minusOp='-') right=rhs
             | left=rhs bitOperator right=rhs
             | left=rhs comparisonOperator right=rhs
             | logicalNot='not' rhs
             | left=rhs logicalOperator right=rhs
             | condition=rhs '?' ifTrue=rhs ':' ifNot=rhs
             | simpleExpression
             ;
    Attributes:
        # encapsulated or with unary operator or with a logical not or just a simple rhs.
        is_encapsulated = False
        is_logical_not = False
        unary_operator = None
        expression = None
        # lhs and rhs combined by an operator
        lhs = None
        binary_operator = None
        rhs = None
        # ternary operator
        condition = None
        if_true = None
        if_not = None
        # simple rhs
        simple_expression = None
    """

    def __init__(self, is_encapsulated=False, unary_operator=None, is_logical_not=False,
                 expression=None, lhs=None, binary_operator=None, rhs=None, condition=None, if_true=None,
                 if_not=None, *args, **kwargs):
        """
        Standard constructor.

        Parameters for superclass (ASTNode) can be passed through :python:`*args` and :python:`**kwargs`.

        :param is_encapsulated: is encapsulated in brackets.
        :type is_encapsulated: bool
        :param unary_operator: combined by unary operator, e.g., ~.
        :type unary_operator: ASTUnaryOperator
        :param is_logical_not: is a negated rhs.
        :type is_logical_not: bool
        :param expression: the rhs either encapsulated in brackets or negated or with a with a unary op, or a simple rhs.
        :type expression: ASTExpression
        :param lhs: the left-hand side rhs.
        :type lhs: ASTExpression
        :param binary_operator: a binary operator, e.g., a comparison operator or a logical operator.
        :type binary_operator: ASTLogicalOperator,ASTComparisonOperator,ASTBitOperator,ASTArithmeticOperator
        :param rhs: the right-hand side rhs
        :type rhs: ASTExpression
        :param condition: the condition of a ternary operator
        :type condition: ASTExpression
        :param if_true: if condition holds, this rhs is executed.
        :type if_true: ASTExpression
        :param if_not: if condition does not hold, this rhs is executed.
        :type if_not: ASTExpression
        """
        super(ASTExpression, self).__init__(*args, **kwargs)
        assert ((binary_operator is None) or (isinstance(binary_operator, ASTArithmeticOperator)
                                              or isinstance(binary_operator, ASTBitOperator)
                                              or isinstance(binary_operator, ASTLogicalOperator)
                                              or isinstance(binary_operator, ASTComparisonOperator))), \
            '(PyNestML.AST.Expression) Wrong type of binary operator provided (%s)!' % type(binary_operator)
        self.is_encapsulated = is_encapsulated
        self.is_logical_not = is_logical_not
        self.unary_operator = unary_operator
        self.expression = expression
        # lhs and rhs combined by an operator
        self.lhs = lhs
        self.binary_operator = binary_operator
        self.rhs = rhs
        # ternary operator
        self.condition = condition
        self.if_true = if_true
        self.if_not = if_not

    def clone(self):
        """
        Return a clone ("deep copy") of this node.

        :return: new AST node instance
        :rtype: ASTExpression
        """
        expression_dup = None
        if self.expression:
            expression_dup = self.expression.clone()
        unary_operator_dup = None
        if self.unary_operator:
            unary_operator_dup = self.unary_operator.clone()
        lhs_dup = None
        if self.lhs:
            lhs_dup = self.lhs.clone()
        binary_operator_dup = None
        if self.binary_operator:
            binary_operator_dup = self.binary_operator.clone()
        rhs_dup = None
        if self.rhs:
            rhs_dup = self.rhs.clone()
        condition_dup = None
        if self.condition:
            condition_dup = self.condition.clone()
        if_true_dup = None
        if self.if_true:
            if_true_dup = self.if_true.clone()
        if_not_dup = None
        if self.if_not:
            if_not_dup = self.if_not.clone()
        dup = ASTExpression(is_encapsulated=self.is_encapsulated,
                            unary_operator=unary_operator_dup,
                            is_logical_not=self.is_logical_not,
                            expression=expression_dup,
                            lhs=lhs_dup,
                            binary_operator=binary_operator_dup,
                            rhs=rhs_dup,
                            condition=condition_dup,
                            if_true=if_true_dup,
                            if_not=if_not_dup,
                            # ASTNode common attributes:
                            source_position=self.source_position,
                            scope=self.scope,
                            comment=self.comment,
                            pre_comments=[s for s in self.pre_comments],
                            in_comment=self.in_comment,
                            post_comments=[s for s in self.post_comments],
                            implicit_conversion_factor=self.implicit_conversion_factor)

        return dup

    def is_expression(self):
        """
        :rtype: bool
        """
        return self.expression is not None

    def get_expression(self):
        """
        Returns the rhs.
        :return: the rhs.
        :rtype: ASTExpression
        """
        return self.expression

    def is_unary_operator(self):
        """
        Returns whether the rhs uses an unary operator.
        :return: True if unary operator, otherwise False.
        :rtype: bool
        """
        return self.unary_operator is not None

    def get_unary_operator(self):
        """
        Returns the unary operator.
        :return: the unary operator.
        :rtype: ASTUnaryOperator.
        """
        return self.unary_operator

    def is_compound_expression(self):
        """
        Returns whether it is a compound rhs, e.g., 10+10
        :return: True if compound rhs, otherwise False.
        :rtype: bool
        """
        return (self.lhs is not None) and (self.rhs is not None) and (self.binary_operator is not None)

    def get_lhs(self):
        """
        Returns the left-hand side rhs.
        :return: the left-hand side rhs.
        :rtype: ASTExpression
        """
        return self.lhs

    def get_rhs(self):
        """
        Returns the right-hand side rhs.
        :return: the right-hand side rhs.
        :rtype: ASTExpression
        """
        return self.rhs

    def get_binary_operator(self):
        """
        Returns the binary operator.
        :return: the binary operator.
        :rtype: one of ASTLogicalOperator,ASTComparisonOperator,ASTBitOperator,ASTArithmeticOperator
        """
        return self.binary_operator

    def is_ternary_operator(self):
        """
        Returns whether it is a ternary operator.
        :return: True if ternary operator, otherwise False.
        :rtype: bool
        """
        return (self.condition is not None) and (self.if_true is not None) and (self.if_not is not None)

    def get_condition(self):
        """
        Returns the condition rhs.
        :return: the condition rhs.
        :rtype: ASTExpression
        """
        return self.condition

    def get_if_true(self):
        """
        Returns the rhs used in the case that the condition holds.
        :return: the if-true condition.
        :rtype: ASTExpression
        """
        return self.if_true

    def get_if_not(self):
        """
        Returns the rhs used in the case that the condition does not hold.
        :return: the if-not condition.
        :rtype: ASTExpression
        """
        return self.if_not

    def get_variables(self):
        """
        Returns a list of all variables as used in this rhs.
        :return: a list of variables.
        :rtype: list(ASTVariable)
        """
        # TODO: extract this to utils
        ret = list()
        if self.is_expression():
            ret.extend(self.get_expression().get_variables())
        elif self.is_compound_expression():
            ret.extend(self.get_lhs().get_variables())
            ret.extend(self.get_rhs().get_variables())
        elif self.is_ternary_operator():
            ret.extend(self.get_condition().get_variables())
            ret.extend(self.get_if_true().get_variables())
            ret.extend(self.get_if_not().get_variables())
        return ret

    def get_units(self):
        """
        Returns a list of all units as use in this rhs.
        :return: a list of all used units.
        :rtype: list(ASTVariable)
        """
        # TODO: extract this to utils
        ret = list()
        if self.is_expression():
            ret.extend(self.get_expression().get_units())
        elif self.is_compound_expression():
            ret.extend(self.get_lhs().get_units())
            ret.extend(self.get_rhs().get_units())
        elif self.is_ternary_operator():
            ret.extend(self.get_condition().get_units())
            ret.extend(self.get_if_true().get_units())
            ret.extend(self.get_if_not().get_units())
        return ret

    def get_function_calls(self):
        """
        Returns a list of all function calls as used in this rhs
        :return: a list of all function calls in this rhs.
        :rtype: list(ASTFunctionCall)
        """
        # TODO: extract this to utils
        ret = list()
        if self.is_expression():
            ret.extend(self.get_expression().get_function_calls())
        elif self.is_compound_expression():
            ret.extend(self.get_lhs().get_function_calls())
            ret.extend(self.get_rhs().get_function_calls())
        elif self.is_ternary_operator():
            ret.extend(self.get_condition().get_function_calls())
            ret.extend(self.get_if_true().get_function_calls())
            ret.extend(self.get_if_not().get_function_calls())
        return ret

    def get_parent(self, ast=None):
        """
        Indicates whether a this node contains the handed over node.
        :param ast: an arbitrary meta_model node.
        :type ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        if self.is_expression():
            if self.get_expression() is ast:
                return self
            if self.get_expression().get_parent(ast) is not None:
                return self.get_expression().get_parent(ast)
        if self.is_unary_operator():
            if self.get_unary_operator() is ast:
                return self
            if self.get_unary_operator().get_parent(ast) is not None:
                return self.get_unary_operator().get_parent(ast)
        if self.is_compound_expression():
            if self.get_lhs() is ast:
                return self
            if self.get_lhs().get_parent(ast) is not None:
                return self.get_lhs().get_parent(ast)
            if self.get_binary_operator() is ast:
                return self
            if self.get_binary_operator().get_parent(ast) is not None:
                return self.get_binary_operator().get_parent(ast)
            if self.get_rhs() is ast:
                return self
            if self.get_rhs().get_parent(ast) is not None:
                return self.get_rhs().get_parent(ast)
        if self.is_ternary_operator():
            if self.get_condition() is ast:
                return self
            if self.get_condition().get_parent(ast) is not None:
                return self.get_condition().get_parent(ast)
            if self.get_if_true() is ast:
                return self
            if self.get_if_true().get_parent(ast) is not None:
                return self.get_if_true().get_parent(ast)
            if self.get_if_not() is ast:
                return self
            if self.get_if_not().get_parent(ast) is not None:
                return self.get_if_not().get_parent(ast)
        return None

    def equals(self, other):
        """
        The equals method.
        :param other: a different object.
        :type other: object
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if not isinstance(other, ASTExpression):
            return False
        # we have to ensure that both either are encapsulated or not
        if self.is_encapsulated + other.is_encapsulated == 1:
            return False
        if self.is_logical_not + other.is_logical_not == 1:
            return False
        if self.is_unary_operator() + other.is_unary_operator() == 1:
            return False
        if self.is_unary_operator() and other.is_unary_operator() and \
                not self.get_unary_operator().equals(other.get_unary_operator()):
            return False
        if self.is_expression() + other.is_expression() == 1:
            return False
        if self.is_expression() and other.is_expression() and not self.get_expression().equals(other.get_expression()):
            return False
        if self.is_compound_expression() + other.is_compound_expression() == 1:
            return False
        if self.is_compound_expression() and other.is_compound_expression() and \
                not (self.get_lhs().equals(other.get_lhs()) and self.get_rhs().equals(other.get_rhs())
                     and self.get_binary_operator().equals(other.get_binary_operator())):
            return False
        if self.is_ternary_operator() + other.is_ternary_operator() == 1:
            return False
        if self.is_ternary_operator() and other.is_ternary_operator() and \
                not (self.get_condition().equals(other.get_condition())
                     and self.get_if_true().equals(other.get_if_true()) and self.get_if_not().equals(other.get_if_not())):
            return False
        return True
