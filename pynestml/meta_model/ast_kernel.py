# -*- coding: utf-8 -*-
#
# ast_kernel.py
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


class ASTKernel(ASTNode):
    """
    This class is used to store kernels.
    Grammar:
        kernel : KERNEL_KEYWORD variable EQUALS expression (COMMA variable EQUALS expression)* (SEMICOLON)?;
    """

    def __init__(self, variables, expressions, *args, **kwargs):
        """
        Standard constructor.

        Parameters for superclass (ASTNode) can be passed through :python:`*args` and :python:`**kwargs`.

        :param variables: the variable corresponding to the kernel
        :type variables: ASTVariable
        :param expressions: the right-hand side
        :type expressions: Union[ASTExpression, ASTSimpleExpression]
        """
        super(ASTKernel, self).__init__(*args, **kwargs)
        self.variables = variables
        self.expressions = expressions

    def clone(self):
        """
        Return a clone ("deep copy") of this node.

        :return: new AST node instance
        :rtype: ASTInputPort
        """
        variables_dup = None
        if self.variables:
            variables_dup = [var.clone() for var in self.variables]
        expressions_dup = None
        if self.expressions:
            expressions_dup = [expr.clone() for expr in self.expressions]
        dup = ASTKernel(variables=variables_dup,
                        expressions=expressions_dup,
                        # ASTNode common attributes:
                        source_position=self.source_position,
                        scope=self.scope,
                        comment=self.comment,
                        pre_comments=[s for s in self.pre_comments],
                        in_comment=self.in_comment,
                        post_comments=[s for s in self.post_comments],
                        implicit_conversion_factor=self.implicit_conversion_factor)

        return dup

    def get_variables(self):
        """
        Returns the variable of the left-hand side.
        :return: the variable
        :rtype: ast_variable
        """
        return self.variables

    def get_variable_names(self):
        """
        Returns the variable of the left-hand side.
        :return: the variable
        :rtype: ast_variable
        """
        return [var.get_complete_name() for var in self.variables]

    def get_expressions(self):
        """
        Returns the right-hand side rhs.
        :return: the rhs
        :rtype: ast_expression
        """
        return self.expressions

    def get_parent(self, ast):
        """
        Indicates whether this node contains the handed over node.
        :param ast: an arbitrary meta_model node.
        :type ast: ASTNode
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: ASTNode or None
        """
        for var in self.get_variables():
            if var is ast:
                return self

            if var.get_parent(ast) is not None:
                return var.get_parent(ast)

        for expr in self.get_expressions():
            if expr is ast:
                return self

            if expr.get_parent(ast) is not None:
                return expr.get_parent(ast)

        return None

    def equals(self, other):
        """
        The equals method.
        :param other: a different object.
        :type other: object
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if not isinstance(other, ASTKernel):
            return False

        for var in self.get_variables():
            if not var in other.get_variables():
                return False

        for var in other.get_variables():
            if not var in self.get_variables():
                return False

        for expr in self.get_expressions():
            if not expr in other.get_expressions():
                return False

        for expr in other.get_expressions():
            if not expr in self.get_expressions():
                return False

        return True
