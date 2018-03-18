#
# ASTOdeEquation.py
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


from pynestml.modelprocessor.ASTNode import ASTNode
from pynestml.modelprocessor.ASTVariable import ASTVariable
from pynestml.modelprocessor.ASTExpression import ASTExpression
from pynestml.modelprocessor.ASTSimpleExpression import ASTSimpleExpression


class ASTOdeEquation(ASTNode):
    """
    This class is used to store ast equations, e.g., V_m' = 10mV + V_m.
    ASTOdeEquation Represents an equation, e.g. "I = exp(t)" or represents an differential equations,
     e.g. "V_m' = V_m+1".
    @attribute lhs      Left hand side, e.g. a Variable.
    @attribute rhs      Expression defining the right hand side.
    Grammar:
        odeEquation : lhs=variable '=' rhs=expression;
    """
    __lhs = None
    __rhs = None

    def __init__(self, _lhs=None, _rhs=None, _sourcePosition=None):
        """
        Standard constructor.
        :param _lhs: an object of type ASTVariable
        :type _lhs: ASTVariable
        :param _rhs: an object of type ASTExpression.
        :type _rhs: ASTExpression or ASTSimpleExpression
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        """
        assert (_lhs is not None and isinstance(_lhs, ASTVariable)), \
            '(PyNestML.AST.OdeEquation) No or wrong type of left-hand variable provided (%s)!' % type(_lhs)
        assert (_rhs is not None and (isinstance(_rhs, ASTExpression) or isinstance(_rhs, ASTSimpleExpression))), \
            '(PyNestML.AST.OdeEquation) No or wrong type of right-hand side expression provided (%s)!' % type(_rhs)
        super(ASTOdeEquation, self).__init__(_sourcePosition)
        self.__lhs = _lhs
        self.__rhs = _rhs
        return

    @classmethod
    def makeASTOdeEquation(cls, _lhs=None, _rhs=None, _sourcePosition=None):
        """
        A factory method used to generate new ASTOdeEquation.
        :param _lhs: an object of type ASTVariable
        :type _lhs: ASTVariable
        :param _rhs: an object of type ASTExpression
        :type _rhs: ASTExpression or ASTSimpleExpression
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        :return a new ASTOdeEquation object.
        :rtype ASTOdeEquation
        """
        return cls(_lhs, _rhs, _sourcePosition)

    def getLhs(self):
        """
        Returns the left-hand side of the equation.
        :return: an object of the ast-variable class.
        :rtype: ASTVariable
        """
        return self.__lhs

    def getRhs(self):
        """
        Returns the left-hand side of the equation.
        :return: an object of the ast-expr class.
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
        if self.getLhs() is _ast:
            return self
        elif self.getLhs().getParent(_ast) is not None:
            return self.getLhs().getParent(_ast)
        if self.getRhs() is _ast:
            return self
        elif self.getRhs().getParent(_ast) is not None:
            return self.getRhs().getParent(_ast)
        return None

    def __str__(self):
        """
        Returns a string representation of the equation.
        :return: a string representing the equation.
        :rtype: str
        """
        return str(self.getLhs()) + '=' + str(self.getRhs())

    def equals(self, _other=None):
        """
        The equals method.
        :param _other: a different object.
        :type _other: object
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if not isinstance(_other, ASTOdeEquation):
            return False
        return self.getLhs().equals(_other.getLhs()) and self.getRhs().equals(_other.getRhs())
