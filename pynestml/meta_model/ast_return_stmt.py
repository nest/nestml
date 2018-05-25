#
# ast_return_stmt.py
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

from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.meta_model.ast_node import ASTNode
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression


class ASTReturnStmt(ASTNode):
    """
    This class is used to store a return statement.
        A ReturnStmt Models the return statement in a function.
        @attribute minus An optional sing
        @attribute definingVariable Name of the variable
        Grammar:
            returnStmt : 'return' expr?;
    Attributes:
          expression (ASTSimpleExpression or ASTExpression): An rhs representing the returned value.
    """

    def __init__(self, expression=None, source_position=None):
        """
        Standard constructor.
        :param expression: an rhs.
        :type expression: ASTExpression
        :param source_position: the position of this element in the source file.
        :type source_position: ASTSourceLocation.
        """
        super(ASTReturnStmt, self).__init__(source_position)
        self.expression = expression

    def has_expression(self):
        """
        Returns whether the return statement has an rhs or not.
        :return: True if has rhs, otherwise False.
        :rtype: bool
        """
        return self.expression is not None

    def get_expression(self):
        """
        Returns the rhs.
        :return: an rhs.
        :rtype: ASTExpression
        """
        return self.expression

    def get_parent(self, ast):
        """
        Indicates whether a this node contains the handed over node.
        :param ast: an arbitrary meta_model node.
        :type ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        if self.has_expression():
            if self.get_expression() is ast:
                return self
            elif self.get_expression().get_parent(ast) is not None:
                return self.get_expression().get_parent(ast)
        return None

    def equals(self, other):
        """
        The equals method.
        :param other: a different object.
        :type other: object
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if not isinstance(other, ASTReturnStmt):
            return False
        return self.get_expression().equals(other.get_expression())
