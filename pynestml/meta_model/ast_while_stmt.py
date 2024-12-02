# -*- coding: utf-8 -*-
#
# ast_while_stmt.py
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

from pynestml.meta_model.ast_stmts_body import ASTStmtsBody
from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_node import ASTNode


class ASTWhileStmt(ASTNode):
    """
    This class is used to store a new while-block.
    Grammar:
        whileStmt : 'while' expr BLOCK_OPEN block BLOCK_CLOSE;
    Attributes:
        condition = None
        block = None
    """

    def __init__(self, condition: ASTExpression, stmts_body: ASTStmtsBody, *args, **kwargs):
        """
        Standard constructor.

        Parameters for superclass (ASTNode) can be passed through :python:`*args` and :python:`**kwargs`.

        :param condition: the condition of the ``while`` loop.
        :type condition: ASTExpression
        :param stmts_body: a body of statements.
        """
        super(ASTWhileStmt, self).__init__(*args, **kwargs)
        self.stmts_body = stmts_body
        self.condition = condition

    def clone(self):
        """
        Return a clone ("deep copy") of this node.

        :return: new AST node instance
        :rtype: ASTWhileStmt
        """
        stmts_body_dup = None
        if self.stmts_body:
            stmts_body_dup = self.stmts_body.clone()
        condition_dup = None
        if self.condition:
            condition_dup = self.condition.clone()
        dup = ASTWhileStmt(stmts_body=stmts_body_dup,
                           condition=condition_dup,
                           # ASTNode common attributes:
                           source_position=self.source_position,
                           scope=self.scope,
                           comment=self.comment,
                           pre_comments=[s for s in self.pre_comments],
                           in_comment=self.in_comment,
                           implicit_conversion_factor=self.implicit_conversion_factor)

        return dup

    def get_condition(self):
        """
        Returns the condition of the block.
        :return: the condition.
        :rtype: ASTExpression
        """
        return self.condition

    def get_stmts_body(self) -> ASTStmtsBody:
        """
        Returns the body of statements.
        :return: the body of statements.
        """
        return self.stmts_body

    def get_children(self) -> List[ASTNode]:
        r"""
        Returns the children of this node, if any.
        :return: List of children of this node.
        """
        children = []
        if self.get_condition():
            children.append(self.get_condition())

        if self.get_stmts_body():
            children.append(self.get_stmts_body())

        return children

    def equals(self, other: ASTNode) -> bool:
        r"""
        The equality method.
        """
        if not isinstance(other, ASTWhileStmt):
            return False
        return self.get_condition().equals(other.get_condition()) and self.get_stmts_body().equals(other.get_stmts_body())
