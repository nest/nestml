# -*- coding: utf-8 -*-
#
# ast_for_stmt.py
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
from pynestml.meta_model.ast_stmts_body import ASTStmtsBody


class ASTForStmt(ASTNode):
    r"""
    This class is used to store a "for" statement.
    """

    def __init__(self, variable, start_from, end_at, step, stmts_body: ASTStmtsBody, *args, **kwargs):
        """
        Standard constructor.

        Parameters for superclass (ASTNode) can be passed through :python:`*args` and :python:`**kwargs`.

        :param variable: the step variable used for iteration.
        :type variable: str
        :param start_from: left bound of the range, i.e., start value.
        :type start_from: ASTExpression
        :param end_at: right bound of the range, i.e., finish value.
        :type end_at: ast_expression
        :param step: the length of a single step.
        :type step: float/int
        :param stmts_body: a body of statements.
        """
        super(ASTForStmt, self).__init__(*args, **kwargs)
        self.variable = variable
        self.start_from = start_from
        self.end_at = end_at
        self.step = step
        self.stmts_body = stmts_body

    def clone(self):
        """
        Return a clone ("deep copy") of this node.

        :return: new AST node instance
        :rtype: ASTForStmt
        """
        variable_dup = None
        if self.variable:
            variable_dup = self.variable
        start_from_dup = None
        if self.start_from:
            start_from_dup = self.start_from.clone()
        end_at_dup = None
        if self.end_at:
            end_at_dup = self.end_at.clone()
        step_dup = None
        if self.step:
            step_dup = self.step
        stmts_body_dup = None
        if self.stmts_body:
            stmts_body_dup = self.stmts_body.clone()
        dup = ASTForStmt(variable=variable_dup,
                         start_from=start_from_dup,
                         end_at=end_at_dup,
                         step=step_dup,
                         stmts_body=stmts_body_dup,
                         # ASTNode common attributes:
                         source_position=self.source_position,
                         scope=self.scope,
                         comment=self.comment,
                         pre_comments=[s for s in self.pre_comments],
                         in_comment=self.in_comment,
                         implicit_conversion_factor=self.implicit_conversion_factor)

        return dup

    def get_variable(self):
        """
        Returns the name of the step variable.
        :return: the name of the step variable.
        :rtype: str
        """
        return self.variable

    def get_start_from(self):
        """
        Returns the from-statement.
        :return: the rhs indicating the start value.
        :rtype: ast_expression
        """
        return self.start_from

    def get_end_at(self):
        """
        Returns the to-statement.
        :return: the rhs indicating the finish value.
        :rtype: ast_expression
        """
        return self.end_at

    def get_step(self):
        """
        Returns the length of a single step.
        :return: the length as a float.
        :rtype: float
        """
        return self.step

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
        if self.get_start_from():
            children.append(self.get_start_from())

        if self.get_end_at():
            children.append(self.get_end_at())

        if self.get_stmts_body():
            children.append(self.get_stmts_body())

        return children

    def equals(self, other: ASTNode) -> bool:
        r"""
        The equality method.
        """
        if not isinstance(other, ASTForStmt):
            return False
        if self.get_variable() != other.get_variable():
            return False
        if not self.get_start_from().equals(other.get_start_from()):
            return False
        if not self.get_end_at().equals(other.get_end_at()):
            return False
        if self.get_step() != other.get_step():
            return False
        return self.get_stmts_body().equals(other.get_stmts_body())
