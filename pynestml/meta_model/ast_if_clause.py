# -*- coding: utf-8 -*-
#
# ast_if_clause.py
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


class ASTIfClause(ASTNode):
    """
    This class is used to store a single if-clause.
    Grammar:
        ifClause : 'if' expr BLOCK_OPEN block;
    Attributes:
        condition = None
        block = None
    """

    def __init__(self, condition, block, *args, **kwargs):
        """
        Standard constructor.

        Parameters for superclass (ASTNode) can be passed through :python:`*args` and :python:`**kwargs`.

        :param condition: the condition of the block.
        :type condition: ASTExpression
        :param block: a block of statements.
        :type block: ASTBlock
        """
        super(ASTIfClause, self).__init__(*args, **kwargs)
        self.block = block
        self.condition = condition

    def clone(self):
        """
        Return a clone ("deep copy") of this node.

        :return: new AST node instance
        :rtype: ASTIfClause
        """
        block_dup = None
        if self.block:
            block_dup = self.block.clone()
        condition_dup = None
        if self.condition:
            condition_dup = self.condition.clone()
        dup = ASTIfClause(condition=condition_dup,
                          block=block_dup,
                          # ASTNode common attributes:
                          source_position=self.source_position,
                          scope=self.scope,
                          comment=self.comment,
                          pre_comments=[s for s in self.pre_comments],
                          in_comment=self.in_comment,
                          post_comments=[s for s in self.post_comments],
                          implicit_conversion_factor=self.implicit_conversion_factor)

        return dup

    def get_condition(self):
        """
        Returns the condition of the block.
        :return: the condition.
        :rtype: ASTExpression
        """
        return self.condition

    def get_block(self):
        """
        Returns the block of statements.
        :return: the block of statements.
        :rtype: ASTBlock
        """
        return self.block

    def get_parent(self, ast):
        """
        Indicates whether a this node contains the handed over node.
        :param ast: an arbitrary meta_model node.
        :type ast: ASTNode
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: Optional[ASTNode]
        """
        if self.get_condition() is ast:
            return self
        if self.get_condition().get_parent(ast) is not None:
            return self.get_condition().get_parent(ast)
        if self.get_block() is ast:
            return self
        if self.get_block().get_parent(ast) is not None:
            return self.get_block().get_parent(ast)
        return None

    def equals(self, other):
        """
        The equals method.
        :param other: a different object.
        :type other: object
        :return: True if equals, otherwise False.
        :rtype: bool
        """
        if not isinstance(other, ASTIfClause):
            return False
        return self.get_condition().equals(other.get_condition()) and self.get_block().equals(other.get_block())
