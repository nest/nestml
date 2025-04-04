# -*- coding: utf-8 -*-
#
# ast_ode_equation.py
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

from typing import List

from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.meta_model.ast_namespace_decorator import ASTNamespaceDecorator


class ASTOdeEquation(ASTNode):
    """
    This class is used to store meta_model equations, e.g., V_m' = 10mV + V_m.
    ASTOdeEquation Represents an equation, e.g. "I = exp(t)" or represents an differential equations,
     e.g. "V_m' = V_m+1".
    @attribute lhs      Left hand side, e.g. a Variable.
    @attribute rhs      Expression defining the right hand side.
    Grammar:
        odeEquation : lhs=variable '=' rhs=rhs;
    Attributes:
        lhs = None
        rhs = None
    """

    def __init__(self, lhs, rhs, decorators=None, *args, **kwargs):
        """
        Standard constructor.

        Parameters for superclass (ASTNode) can be passed through :python:`*args` and :python:`**kwargs`.

        :param lhs: left-hand side variable
        :type lhs: ASTVariable
        :param rhs: right-hand side expression
        :type rhs: Union[ASTExpression, ASTSimpleExpression]
        """
        super(ASTOdeEquation, self).__init__(*args, **kwargs)
        assert isinstance(lhs, ASTVariable)
        assert isinstance(rhs, ASTExpression) or isinstance(rhs, ASTSimpleExpression)
        if decorators is None:
            decorators = []
        self.lhs = lhs
        self.rhs = rhs
        self.decorators = decorators

    def clone(self):
        """
        Return a clone ("deep copy") of this node.

        :return: new AST node instance
        :rtype: ASTOdeEquation
        """
        decorators_dup = None
        if self.decorators:
            decorators_dup = [dec.clone() if isinstance(dec, ASTNamespaceDecorator) else str(dec) for dec in
                              self.decorators]

        dup = ASTOdeEquation(lhs=self.lhs.clone(),
                             rhs=self.rhs.clone(),
                             decorators=decorators_dup,
                             # ASTNode common attributes:
                             source_position=self.source_position,
                             scope=self.scope,
                             comment=self.comment,
                             pre_comments=[s for s in self.pre_comments],
                             in_comment=self.in_comment,
                             implicit_conversion_factor=self.implicit_conversion_factor)

        return dup

    def get_decorators(self):
        """
        """
        return self.decorators

    def get_lhs(self):
        """
        Returns the left-hand side of the equation.
        :return: an object of the meta_model-variable class.
        :rtype: ASTVariable
        """
        return self.lhs

    def get_rhs(self):
        """
        Returns the left-hand side of the equation.
        :return: an object of the meta_model-expr class.
        :rtype: Union[ASTExpression, ASTSimpleExpression]
        """
        return self.rhs

    def get_children(self) -> List[ASTNode]:
        r"""
        Returns the children of this node, if any.
        :return: List of children of this node.
        """
        children = []
        if self.get_lhs():
            children.append(self.get_lhs())

        if self.get_rhs():
            children.append(self.get_rhs())

        return children

    def equals(self, other: ASTNode) -> bool:
        r"""
        The equality method.
        """
        if not isinstance(other, ASTOdeEquation):
            return False
        return self.get_lhs().equals(other.get_lhs()) and self.get_rhs().equals(other.get_rhs())
