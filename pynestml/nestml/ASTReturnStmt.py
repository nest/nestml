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

from pynestml.nestml.ASTExpression import ASTExpression
from pynestml.nestml.ASTElement import ASTElement
from pynestml.nestml.ASTSimpleExpression import ASTSimpleExpression


class ASTReturnStmt(ASTElement):
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

    def __init__(self, _expression=None, _sourcePosition=None):
        """
        Standard constructor.
        :param _expression: an expression.
        :type _expression: ASTExpression
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        """
        assert (_expression is None or isinstance(_expression, ASTExpression)
                or isinstance(_expression, ASTSimpleExpression)), \
            '(PyNestML.AST.ReturnStmt) Wrong type of return statement provided (%s)!' % type(_expression)
        super(ASTReturnStmt, self).__init__(_sourcePosition)
        self.__expression = _expression

    @classmethod
    def makeASTReturnStmt(cls, _expression=None, _sourcePosition=None):
        """
        Factory method of the ASTReturnStmt class.
        :param _expression: an optional return expression.
        :type _expression: ASTExpression
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        :return: a new ASTReturnStmt object.
        :rtype: ASTReturnStmt
        """
        return cls(_expression, _sourcePosition)

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

    def printAST(self):
        """
        Returns a string representation of the return statement.
        :return: a string representation
        :rtype: str
        """
        return 'return ' + (self.getExpression().printAST() if self.getExpression() is not None else '')

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
