# -*- coding: utf-8 -*-
#
# ast_small_stmt.py
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
from pynestml.meta_model.ast_assignment import ASTAssignment
from pynestml.meta_model.ast_declaration import ASTDeclaration
from pynestml.meta_model.ast_function_call import ASTFunctionCall
from pynestml.meta_model.ast_include_stmt import ASTIncludeStmt

from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_return_stmt import ASTReturnStmt


class ASTSmallStmt(ASTNode):
    """
    This class is used to store small statements, e.g., a declaration.

    Attributes:
        assignment (ast_assignment): A assignment reference.
        function_call (ast_function_call): A function call reference.
        declaration (ast_declaration): A declaration reference.
        return_stmt (ast_return_stmt): A reference to the returns statement.
    """

    def __init__(self, assignment: Optional[ASTAssignment] = None, function_call: Optional[ASTFunctionCall] = None, declaration: Optional[ASTDeclaration] = None, return_stmt: Optional[ASTReturnStmt] = None, include_stmt: Optional[ASTIncludeStmt] = None, *args, **kwargs):
        """
        Standard constructor.

        Parameters for superclass (ASTNode) can be passed through :python:`*args` and :python:`**kwargs`.

        :param assignment: an meta_model-assignment object.
        :param function_call: an meta_model-function call object.
        :param declaration: an meta_model-declaration object.
        :param return_stmt: an meta_model-return statement object.
        """
        super(ASTSmallStmt, self).__init__(*args, **kwargs)
        self.assignment = assignment
        self.function_call = function_call
        self.declaration = declaration
        self.return_stmt = return_stmt
        self.include_stmt = include_stmt
        assert self.assignment or self.function_call or self.declaration or self.return_stmt or self.include_stmt

    def clone(self):
        """
        Return a clone ("deep copy") of this node.

        :return: new AST node instance
        :rtype: ASTSmallStmt
        """
        assignment_dup = None
        if self.assignment:
            assignment_dup = self.assignment.clone()
        function_call_dup = None
        if self.function_call:
            function_call_dup = self.function_call.clone()
        declaration_dup = None
        if self.declaration:
            declaration_dup = self.declaration.clone()
        return_stmt_dup = None
        if self.return_stmt:
            return_stmt_dup = self.return_stmt.clone()
        include_stmt_dup = None
        if self.include_stmt:
            include_stmt_dup = self.include_stmt.clone()
        dup = ASTSmallStmt(assignment=assignment_dup,
                           function_call=function_call_dup,
                           declaration=declaration_dup,
                           return_stmt=return_stmt_dup,
                           include_stmt=include_stmt_dup,
                           # ASTNode common attributes:
                           source_position=self.source_position,
                           scope=self.scope,
                           comment=self.comment,
                           pre_comments=[s for s in self.pre_comments],
                           in_comment=self.in_comment,
                           implicit_conversion_factor=self.implicit_conversion_factor)

        return dup

    def is_assignment(self):
        """
        Returns whether it is an assignment statement or not.
        :return: True if assignment, False else.
        :rtype: bool
        """
        return self.assignment is not None

    def get_assignment(self):
        """
        Returns the assignment.
        :return: the assignment statement.
        :rtype: ast_assignment
        """
        return self.assignment

    def is_function_call(self):
        """
        Returns whether it is an function call or not.
        :return: True if function call, False else.
        :rtype: bool
        """
        return self.function_call is not None

    def get_function_call(self):
        """
        Returns the function call.
        :return: the function call statement.
        :rtype: ast_function_call
        """
        return self.function_call

    def is_declaration(self):
        """
        Returns whether it is a declaration statement or not.
        :return: True if declaration, False else.
        :rtype: bool
        """
        return self.declaration is not None

    def get_declaration(self):
        """
        Returns the assignment.
        :return: the declaration statement.
        :rtype: ast_declaration
        """
        return self.declaration

    def is_return_stmt(self):
        """
        Returns whether it is a return statement or not.
        :return: True if return stmt, False else.
        :rtype: bool
        """
        return self.return_stmt is not None

    def get_return_stmt(self):
        """
        Returns the return statement.
        :return: the return statement.
        :rtype: ast_return_stmt
        """
        return self.return_stmt

    def is_include_stmt(self) -> bool:
        """
        Returns whether it is a include statement or not.
        :return: True if include stmt, False else.
        """
        return self.include_stmt is not None

    def get_include_stmt(self) -> Optional[ASTIncludeStmt]:
        """
        Returns the include statement.
        :return: the include statement.
        """
        return self.include_stmt

    def get_children(self) -> List[ASTNode]:
        r"""
        Returns the children of this node, if any.
        :return: List of children of this node.
        """
        if self.is_assignment():
            return [self.get_assignment()]

        if self.is_function_call():
            return [self.get_function_call()]

        if self.is_declaration():
            return [self.get_declaration()]

        if self.is_return_stmt():
            return [self.get_return_stmt()]

        if self.is_include_stmt():
            return [self.get_include_stmt()]

        return []

    def equals(self, other: ASTNode) -> bool:
        r"""
        The equality method.
        """
        if not isinstance(other, ASTSmallStmt):
            return False
        if self.is_function_call() + other.is_function_call() == 1:
            return False
        if self.is_function_call() and other.is_function_call() and \
                not self.get_function_call().equals(other.get_function_call()):
            return False
        if self.is_assignment() + other.is_assignment() == 1:
            return False
        if self.is_assignment() and other.is_assignment() and not self.get_assignment().equals(other.get_assignment()):
            return False
        if self.is_declaration() + other.is_declaration() == 1:
            return False
        if self.is_declaration() and other.is_declaration() and not self.get_declaration().equals(
                other.get_declaration()):
            return False
        if self.is_return_stmt() + other.is_return_stmt() == 1:
            return False
        if self.is_return_stmt() and other.is_return_stmt() and not self.get_return_stmt().equals(
                other.get_return_stmt()):
            return False
        if self.is_include_stmt() + other.is_include_stmt() == 1:
            return False
        if self.is_include_stmt() and other.is_include_stmt() and not self.get_include_stmt().equals(
                other.get_include_stmt()):
            return False
        return True
