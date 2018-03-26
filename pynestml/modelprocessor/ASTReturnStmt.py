#
# ASTReturnStmt.py
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

from pynestml.modelprocessor.ASTExpression import ASTExpression
from pynestml.modelprocessor.ASTNode import ASTNode
from pynestml.modelprocessor.ASTSimpleExpression import ASTSimpleExpression


class ASTReturnStmt(ASTNode):
    """
    This class is used to store a return statement.
        A ReturnStmt Models the return statement in a function.
        @attribute minus An optional sing
        @attribute definingVariable Name of the variable
        Grammar:
            returnStmt : 'return' expr?;
    Attributes:
          __expression (ASTSimpleExpression or ASTExpression): An expression representing the returned value.
    """
    __expression = None

    def __init__(self, expression=None, source_position=None):
        """
        Standard constructor.
        :param expression: an expression.
        :type expression: ASTExpression
        :param source_position: the position of this element in the source file.
        :type source_position: ASTSourcePosition.
        """
        assert (expression is None or isinstance(expression, ASTExpression)
                or isinstance(expression, ASTSimpleExpression)), \
            '(PyNestML.AST.ReturnStmt) Wrong type of return statement provided (%s)!' % type(expression)
        super(ASTReturnStmt, self).__init__(source_position)
        self.__expression = expression

    def hasExpression(self):
        """
        Returns whether the return statement has an expression or not.
        :return: True if has expression, otherwise False.
        :rtype: bool
        """
        return self.__expression is not None

    def getExpression(self):
        """
        Returns the expression.
        :return: an expression.
        :rtype: ASTExpression
        """
        return self.__expression

    def getParent(self, _ast=None):
        """
        Indicates whether a this node contains the handed over node.
        :param _ast: an arbitrary ast node.
        :type _ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        if self.hasExpression():
            if self.getExpression() is _ast:
                return self
            elif self.getExpression().getParent(_ast) is not None:
                return self.getExpression().getParent(_ast)
        return None

    def __str__(self):
        """
        Returns a string representation of the return statement.
        :return: a string representation
        :rtype: str
        """
        return 'return ' + (str(self.getExpression()) if self.hasExpression() else '')

    def equals(self, _other=None):
        """
        The equals method.
        :param _other: a different object.
        :type _other: object
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if not isinstance(_other, ASTReturnStmt):
            return False
        return self.getExpression().equals(_other.getExpression())
