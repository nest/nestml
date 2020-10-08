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
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_expression import ASTExpression


class ASTForStmt(ASTNode):
    """
    This class is used to store a for-block.
    Grammar:
        forStmt : 'for' var=NAME 'in' vrom=rhs
                    '...' to=rhs 'step' step=signedNumericLiteral BLOCK_OPEN block BLOCK_CLOSE;
    Attributes:
        variable = None
        start_from = None
        end_at = None
        step = None
        block = None
    """

    def __init__(self, variable, start_from, end_at, step, block, *args, **kwargs):
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
        :param block: a block of statements.
        :type block: ast_block
        """
        super(ASTForStmt, self).__init__(*args, **kwargs)
        self.block = block
        self.step = step
        self.end_at = end_at
        self.start_from = start_from
        self.variable = variable

    def clone(self):
        """
        Return a clone ("deep copy") of this node.

        :return: new AST node instance
        :rtype: ASTForStmt
        """
        variable_dup = None
        if self.variable:
            variable_dup = self.variable.clone()
        start_from_dup = None
        if self.start_from:
            start_from_dup = self.start_from.clone()
        end_at_dup = None
        if self.end_at:
            end_at_dup = self.end_at.clone()
        step_dup = None
        if self.step:
            step_dup = self.step.clone()
        block_dup = None
        if self.block:
            block_dup = self.block.clone()
        dup = ASTForStmt(variable=variable_dup,
                         start_from=start_from_dup,
                         end_at=end_at_dup,
                         step=step_dup,
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

    def get_block(self):
        """
        Returns the block of statements.
        :return: the block of statements.
        :rtype: ast_block
        """
        return self.block

    def get_parent(self, ast):
        """
        Indicates whether a this node contains the handed over node.
        :param ast: an arbitrary meta_model node.
        :type ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        if self.get_start_from() is ast:
            return self
        if self.get_start_from().get_parent(ast) is not None:
            return self.get_start_from().get_parent(ast)
        if self.get_end_at() is ast:
            return self
        if self.get_end_at().get_parent(ast) is not None:
            return self.get_end_at().get_parent(ast)
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
        :return: True if equal, otherwise False.
        :rtype: bool
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
        return self.get_block().equals(other.get_block())
