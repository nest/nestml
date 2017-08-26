"""
/*
 *  ASTReturnStmt.py
 *
 *  This file is part of NEST.
 *
 *  Copyright (C) 2004 The NEST Initiative
 *
 *  NEST is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  NEST is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with NEST.  If not, see <http://www.gnu.org/licenses/>.
 *
 */
@author kperun
"""
from pynestml.src.main.python.org.nestml.ast.ASTExpression import ASTExpression


class ASTReturnStmt:
    """
    This class is used to store a return statement.
        A ReturnStmt Models the return statement in a function.
        @attribute minus An optional sing
        @attribute definingVariable Name of the variable
        Grammar:
            returnStmt : 'return' expr?;       
    """
    __expression = None

    def __init__(self, _expression=None):
        """
        Standard constructor.
        :param _expression: an expression.
        :type _expression: ASTExpression
        """
        self.__expression = _expression

    @classmethod
    def makeASTReturnStmt(cls, _expression=None):
        """
        Factory method of the ASTReturnStmt class.
        :param _expression: an optional return expression.
        :type _expression: ASTExpression
        :return: a new ASTReturnStmt object.
        :rtype: ASTReturnStmt
        """
        assert (_expression is None or isinstance(_expression, ASTExpression))
        return cls(_expression)

    def hasExpr(self):
        """
        Returns whether the return statement has an expression or not.
        :return: True if has expression, otherwise False.
        :rtype: bool
        """
        return self.__expression is not None

    def getExpr(self):
        """
        Returns the expression.
        :return: an expression.
        :rtype: ASTExpression
        """
        return self.__expression

    def printAST(self):
        """
        Returns a string representation of the return statement.
        :return: a string representation
        :rtype: str
        """
        return 'return ' + (self.getExpr().printAST() if self.getExpr() is not None else '')
