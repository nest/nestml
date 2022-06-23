# -*- coding: utf-8 -*-
#
# ast_logical_operator.py
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
from pynestml.meta_model.ast_node import ASTNode


class ASTLogicalOperator(ASTNode):
    """
    This class is used to store a single logical operator.
    Grammar:
        logicalOperator : (logicalAnd='and' | logicalOr='or');
    Attributes:
        is_logical_and = False
        is_logical_or = False
    """

    def __init__(self, is_logical_and=False, is_logical_or=False, *args, **kwargs):
        """
        Standard constructor.

        Parameters for superclass (ASTNode) can be passed through :python:`*args` and :python:`**kwargs`.

        :param is_logical_and: is logical and.
        :type is_logical_and: bool
        :param is_logical_or: is logical or.
        :type is_logical_or: bool
        """
        assert (is_logical_and ^ is_logical_or), \
            '(PyNestML.AST.LogicalOperator) Logical operator not correctly specified!'
        super(ASTLogicalOperator, self).__init__(*args, **kwargs)
        self.is_logical_and = is_logical_and
        self.is_logical_or = is_logical_or

    def clone(self):
        """
        Return a clone ("deep copy") of this node.

        :return: new AST node instance
        :rtype: ASTLogicalOperator
        """
        dup = ASTLogicalOperator(is_logical_and=self.is_logical_and,
                                 is_logical_or=self.is_logical_or,
                                 # ASTNode common attributes:
                                 source_position=self.source_position,
                                 scope=self.scope,
                                 comment=self.comment,
                                 pre_comments=[s for s in self.pre_comments],
                                 in_comment=self.in_comment,
                                 post_comments=[s for s in self.post_comments],
                                 implicit_conversion_factor=self.implicit_conversion_factor)

        return dup

    def get_parent(self, ast):
        """
        Indicates whether a this node contains the handed over node.
        :param ast: an arbitrary meta_model node.
        :type ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        return None

    def equals(self, other):
        """
        The equals method.
        :param other: a different object.
        :type other: object
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if not isinstance(other, ASTLogicalOperator):
            return False
        return self.is_logical_and == other.is_logical_and and self.is_logical_or == other.is_logical_or
