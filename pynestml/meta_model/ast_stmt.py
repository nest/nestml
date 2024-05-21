# -*- coding: utf-8 -*-
#
# ast_stmt.py
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

from typing import List, Optional

from pynestml.meta_model.ast_node import ASTNode


class ASTStmt(ASTNode):
    """
    Stores a reference to either small or compound statement.
    Grammar:
        stmt : smallStmt | compoundStmt;
    Attributes:
        small_stmt = None
        compound_stmt = None
    """

    def __init__(self, small_stmt, compound_stmt, *args, **kwargs):
        """
        Standard constructor.

        Parameters for superclass (ASTNode) can be passed through :python:`*args` and :python:`**kwargs`.

        :param small_stmt: small statement AST node
        :type small_stmt: ASTSmallStmt
        :param compound_stmt: compound statement AST node
        :type compound_stmt: ASTCompoundStmt
        """
        super(ASTStmt, self).__init__(*args, **kwargs)
        self.small_stmt = small_stmt
        self.compound_stmt = compound_stmt

    def clone(self):
        """
        Return a clone ("deep copy") of this node.

        :return: new AST node instance
        :rtype: ASTStmt
        """
        small_stmt_dup = None
        if self.small_stmt:
            small_stmt_dup = self.small_stmt.clone()
        compound_stmt_dup = None
        if self.compound_stmt:
            compound_stmt_dup = self.compound_stmt.clone()
        dup = ASTStmt(small_stmt=small_stmt_dup,
                      compound_stmt=compound_stmt_dup,
                      # ASTNode common attributes:
                      source_position=self.source_position,
                      scope=self.scope,
                      comment=self.comment,
                      pre_comments=[s for s in self.pre_comments],
                      in_comment=self.in_comment,
                      implicit_conversion_factor=self.implicit_conversion_factor)

        return dup

    def is_small_stmt(self):
        return self.small_stmt is not None

    def is_compound_stmt(self):
        return self.compound_stmt is not None

    def get_children(self) -> List[ASTNode]:
        r"""
        Returns the children of this node, if any.
        :return: List of children of this node.
        """
        if self.small_stmt:
            return [self.small_stmt]

        if self.compound_stmt:
            return [self.compound_stmt]

        return []

    def equals(self, other: ASTNode) -> bool:
        r"""
        The equality method.
        """
        if not isinstance(other, ASTStmt):
            return False
        if self.is_small_stmt() and other.is_small_stmt():
            return self.small_stmt.equals(other.small_stmt)
        if self.is_compound_stmt() and other.is_compound_stmt():
            return self.compound_stmt.equals(other.compound_stmt)
