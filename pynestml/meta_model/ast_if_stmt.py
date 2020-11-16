# -*- coding: utf-8 -*-
#
# ast_if_stmt.py
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


class ASTIfStmt(ASTNode):
    """
    This class is used to store a single if block.
    Grammar:
        ifStmt : ifClause
                    elifClause*
                    (elseClause)?
                    BLOCK_CLOSE;
    Attributes:
        if_clause = None
        elif_clauses = None
        else_clause = None
    """

    def __init__(self, if_clause, elif_clauses=None, else_clause=None, *args, **kwargs):
        """
        Standard constructor.

        Parameters for superclass (ASTNode) can be passed through :python:`*args` and :python:`**kwargs`.

        :param if_clause: the if-clause
        :type if_clause: ast_if_clause
        :param elif_clauses: (optional) list of elif clauses
        :type elif_clauses: Optional[List[ASTElifClause]]
        :param else_clause: (optional) else clause
        :type else_clause: Optional[ASTElseClause]
        """
        super(ASTIfStmt, self).__init__(*args, **kwargs)
        if elif_clauses is None:
            elif_clauses = []
        assert isinstance(elif_clauses, list), \
            '(PyNestML.ASTIfStmt) Wrong type of elif-clauses provided (%s)!' % type(elif_clauses)
        self.else_clause = else_clause
        self.if_clause = if_clause
        self.elif_clauses = elif_clauses

    def clone(self):
        """
        Return a clone ("deep copy") of this node.

        :return: new AST node instance
        :rtype: ASTIfStmt
        """
        if_clause_dup = None
        if self.if_clause:
            if_clause_dup = self.if_clause.clone()
        elif_clauses_dup = None
        if self.elif_clauses:
            elif_clauses_dup = [elif_clause.clone() for elif_clause in self.elif_clauses]
        else_clause_dup = None
        if self.else_clause:
            else_clause_dup = self.else_clause.clone()
        dup = ASTIfStmt(if_clause=if_clause_dup,
                        elif_clauses=elif_clauses_dup,
                        else_clause=else_clause_dup,
                        # ASTNode common attributes:
                        source_position=self.source_position,
                        scope=self.scope,
                        comment=self.comment,
                        pre_comments=[s for s in self.pre_comments],
                        in_comment=self.in_comment,
                        post_comments=[s for s in self.post_comments],
                        implicit_conversion_factor=self.implicit_conversion_factor)

        return dup

    def get_if_clause(self):
        """
        Returns the if-clause.
        :return: the if clause
        :rtype: ASTfClause
        """
        return self.if_clause

    def has_elif_clauses(self):
        """
        Returns whether object contains elif clauses.
        :return: True if at leas one elif clause, False else.
        :rtype: bool
        """
        return len(self.elif_clauses) > 0

    def get_elif_clauses(self):
        """
        Returns a list of elif-clauses.
        :return: a list of elif-clauses.
        :rtype: List[ASTElifClause]
        """
        return self.elif_clauses

    def has_else_clause(self):
        """
        Returns whether object contains elif clauses.
        :return: True if object contains an else-clause, False else.
        :rtype: bool
        """
        return self.else_clause is not None

    def get_else_clause(self):
        """
        Returns the else-clause.
        :return: the else-clause.
        :rtype: ASTElseClause
        """
        return self.else_clause

    def get_parent(self, ast):
        """
        Indicates whether a this node contains the handed over node.
        :param ast: an arbitrary meta_model node.
        :type ast: ASTNode
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: Optional[ASTNode]
        """
        if self.get_if_clause() is ast:
            return self
        if self.get_if_clause().get_parent(ast) is not None:
            return self.get_if_clause().get_parent(ast)
        for elifClause in self.get_elif_clauses():
            if elifClause is ast:
                return self
            if elifClause.get_parent(ast) is not None:
                return elifClause.get_parent(ast)
        if self.has_else_clause():
            if self.get_else_clause() is ast:
                return self
            if self.get_else_clause().get_parent(ast) is not None:
                return self.get_else_clause().get_parent(ast)
        return None

    def equals(self, other):
        """
        The equals method.
        :param other: a different object.
        :type other: object
        :return: True if equals, otherwise False.
        :rtype: bool
        """
        if not isinstance(other, ASTIfStmt):
            return False
        if not self.get_if_clause().equals(other.get_if_clause()):
            return False
        if len(self.get_elif_clauses()) != len(other.get_elif_clauses()):
            return False
        my_elif_clauses = self.get_elif_clauses()
        your_elif_clauses = other.get_elif_clauses()
        for i in range(0, len(my_elif_clauses)):
            if not my_elif_clauses[i].equals(your_elif_clauses[i]):
                return False
        if self.has_else_clause() + other.has_else_clause() == 1:
            return False
        if self.has_else_clause() and other.has_else_clause() and not self.get_else_clause().equals(
                other.get_else_clause()):
            return False
        return True
