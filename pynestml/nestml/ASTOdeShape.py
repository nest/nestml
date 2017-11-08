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

from pynestml.nestml.ASTExpression import ASTExpression
from pynestml.nestml.ASTSimpleExpression import ASTSimpleExpression
from pynestml.nestml.ASTVariable import ASTVariable
from pynestml.nestml.ASTElement import ASTElement


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
        :type _rhs: ASTExpression or ASTSimpleExpression
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        """
        assert (_lhs is not None and (isinstance(_lhs, ASTVariable) or isinstance(_lhs, ASTSimpleExpression))), \
            '(PyNestML.AST.OdeShape) No or wrong type of left-hand side variable provided (%s)!' % type(_lhs)
        assert (_rhs is not None and (isinstance(_rhs, ASTExpression) or isinstance(_rhs, ASTSimpleExpression))), \
            '(PyNestML.AST.OdeShape) No or wrong type of right-hand side expression provided (%s)!' % type(_rhs)
        super(ASTOdeShape, self).__init__(_sourcePosition)
        self.__lhs = _lhs
        self.__rhs = _rhs
        return

    @classmethod
    def makeASTOdeShape(cls, _lhs=None, _rhs=None, _sourcePosition=None):
        """
        Factory method of ASTOdeShape.
        :param _lhs: the variable corresponding to the shape
        :type _lhs: ASTVariable
        :param _rhs: the right-hand side expression
        :type _rhs: ASTExpression or ASTSimpleExpression
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

    def getParent(self, _ast=None):
        """
        Indicates whether a this node contains the handed over node.
        :param _ast: an arbitrary ast node.
        :type _ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        if self.getVariable() is _ast:
            return self
        elif self.getVariable().getParent(_ast) is not None:
            return self.getVariable().getParent(_ast)
        if self.getExpression() is _ast:
            return self
        elif self.getExpression().getParent(_ast) is not None:
            return self.getExpression().getParent(_ast)
        return None

    def __str__(self):
        """
        Returns a string representation of the shape.
        :return: a string representation.
        :rtype: str
        """
        return 'shape ' + str(self.getVariable()) + ' = ' + str(self.getExpression())

    def equals(self, _other=None):
        """
        The equals method.
        :param _other: a different object.
        :type _other: object
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if not isinstance(_other, ASTOdeShape):
            return False
        return self.getVariable().equals(_other.getVariable()) and self.getExpression().equals(_other.getExpression())
