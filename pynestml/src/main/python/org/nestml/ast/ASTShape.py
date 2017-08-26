"""
/*
 *  ASTShape.py
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
from pynestml.src.main.python.org.nestml.ast.ASTVariable import ASTVariable


class ASTShape:
    """
    This class is used to store shapes. 
    Grammar:
        shape : 'shape' lhs=variable '=' rhs=expr;
    """
    __lhs = None
    __rhs = None

    def __init__(self, _lhs=None, _rhs=None):
        """
        Standard constructor of ASTShape.
        :param _lhs: the variable corresponding to the shape 
        :type _lhs: ASTVariable
        :param _rhs: the right-hand side expression
        :type _rhs: ASTExpression
        """
        self.__lhs = _lhs
        self.__rhs = _rhs

    @classmethod
    def makeASTShape(cls, _lhs=None, _rhs=None):
        """
        Factory method of ASTShape.
        :param _lhs: the variable corresponding to the shape
        :type _lhs: ASTVariable
        :param _rhs: the right-hand side expression
        :type _rhs: ASTExpression
        :return: a new ASTShape object
        :rtype: ASTShape
        """
        assert (
            _lhs is not None and isinstance(_lhs, ASTVariable)), '(PyNESTML.AST) No or wrong shape variable provided.'
        assert (
            _rhs is not None and isinstance(_rhs,
                                            ASTExpression)), '(PyNESTML.AST) No or wrong shape expression provided.'
        return cls(_lhs, _rhs)

    def getVariable(self):
        """
        Returns the variable of the left-hand side.
        :return: the variable
        :rtype: ASTVariable
        """
        return self.__lhs

    def getExpression(self):
        """
        Returns the right-hand side expression.
        :return: the expression
        :rtype: ASTExpression
        """
        return self.__rhs

    def printAST(self):
        """
        Returns a string representation of the shape.
        :return: a string representation.
        :rtype: str
        """
        return 'shape ' + self.getVariable().printAST() + ' = ' + self.getExpression().printAST()
