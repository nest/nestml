# -*- coding: utf-8 -*-
#
# ast_stmts_body.py
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


class ASTStmtsBody(ASTNode):
    """
    This class is used to store a single block of declarations, i.e., statements.
    Grammar:
        block : ( smallStmt | compoundStmt | NEWLINE )*;
    Attribute:
        stmts = None
    """

    def __init__(self, stmts, *args, **kwargs):
        """
        Standard constructor.

        Parameters for superclass (ASTNode) can be passed through :python:`*args` and :python:`**kwargs`.

        :param stmts: a list of statements
        :type stmts: List[Union[ASTSmallStmt, ASTCompoundStmt]]
        """
        from pynestml.meta_model.ast_stmt import ASTStmt
        assert (stmts is not None and isinstance(stmts, list)), \
            '(PyNestML.ASTBlock) No or wrong type of statements provided (%s)!' % type(stmts)
        for stmt in stmts:
            assert (stmt is not None and isinstance(stmt, ASTStmt)), \
                '(PyNestML.ASTBlock) No or wrong type of statement provided (%s)!' % type(stmt)

        super(ASTStmtsBody, self).__init__(*args, **kwargs)
        self.stmts = stmts

    def clone(self):
        """
        Return a clone ("deep copy") of this node.

        :return: new AST node instance
        :rtype: ASTBlock
        """
        stmts_dup = [stmt.clone() for stmt in self.stmts]
        dup = ASTStmtsBody(stmts_dup,
                           # ASTNode common attriutes:
                           source_position=self.source_position,
                           scope=self.scope,
                           comment=self.comment,
                           pre_comments=[s for s in self.pre_comments],
                           in_comment=self.in_comment,
                           implicit_conversion_factor=self.implicit_conversion_factor)

        return dup

    def get_stmts(self):
        """
        Returns the list of statements.
        :return: list of stmts.
        :rtype: list(ASTSmallStmt/ASTCompoundStmt)
        """
        return self.stmts

    def add_stmt(self, stmt):
        """
        Adds a single statement to the list of statements.
        :param stmt: a statement
        :type stmt: ASTSmallStmt,ASTCompoundStmt
        """
        self.stmts.append(stmt)

    def delete_stmt(self, stmt):
        """
        Deletes the handed over statement.
        :param stmt:
        :type stmt:
        :return: True if deleted, otherwise False.
        :rtype: bool
        """
        self.stmts.remove(stmt)

    def get_children(self) -> List[ASTNode]:
        r"""
        Returns the children of this node, if any.
        :return: List of children of this node.
        """
        return self.get_stmts()

    def equals(self, other: ASTNode) -> bool:
        r"""
        The equality method.
        """
        if not isinstance(other, ASTStmtsBody):
            return False
        if len(self.get_stmts()) != len(other.get_stmts()):
            return False
        my_stmt = self.get_stmts()
        your_stmts = other.get_stmts()
        for i in range(0, len(self.get_stmts())):
            if not my_stmt[i].equals(your_stmts[i]):
                return False
        return True
