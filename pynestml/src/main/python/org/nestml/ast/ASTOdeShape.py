#
# ASTOdeShape.py
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

from pynestml.src.main.python.org.nestml.ast.ASTExpression import ASTExpression
from pynestml.src.main.python.org.nestml.ast.ASTVariable import ASTVariable
from pynestml.src.main.python.org.nestml.ast.ASTElement import ASTElement


class ASTOdeShape(ASTElement):
    """
    This class is used to store shapes. 
    Grammar:
        odeShape : 'shape' lhs=variable '=' rhs=expr;
    """
    __lhs = None
    __rhs = None

    def __init__(self, _lhs=None, _rhs=None, _sourcePosition=None):
        """
        Standard constructor of ASTOdeShape.
        :param _lhs: the variable corresponding to the shape 
        :type _lhs: ASTVariable
        :param _rhs: the right-hand side expression
        :type _rhs: ASTExpression
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        """
        assert (_lhs is not None and isinstance(_lhs, ASTVariable)), \
            '(PyNestML.AST.OdeShape) No or wrong type of left-hand side variable provided (%s)!' % type(_lhs)
        assert (_rhs is not None and isinstance(_rhs, ASTExpression)), \
            '(PyNestML.AST.OdeShape) No or wrong type of right-hand side expression provided (%s)!' % type(_rhs)
        super(ASTOdeShape, self).__init__(_sourcePosition)
        self.__lhs = _lhs
        self.__rhs = _rhs

    @classmethod
    def makeASTOdeShape(cls, _lhs=None, _rhs=None, _sourcePosition=None):
        """
        Factory method of ASTOdeShape.
        :param _lhs: the variable corresponding to the shape
        :type _lhs: ASTVariable
        :param _rhs: the right-hand side expression
        :type _rhs: ASTExpression
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        :return: a new ASTShape object
        :rtype: ASTOdeShape
        """
        return cls(_lhs, _rhs, _sourcePosition)

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
