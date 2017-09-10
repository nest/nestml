"""
/*
 *  ASTOdeEquation.py
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
from pynestml.src.main.python.org.nestml.ast.ASTElement import ASTElement
from pynestml.src.main.python.org.nestml.ast.ASTDerivative import ASTDerivative
from pynestml.src.main.python.org.nestml.ast.ASTExpression import ASTExpression


class ASTOdeEquation(ASTElement):
    """
    This class is used to store ast equations, e.g., V_m' = 10mV + V_m.
    ASTOdeEquation Represents an equation, e.g. "I = exp(t)" or represents an differential equations,
     e.g. "V_m' = V_m+1".
    @attribute lhs      Left hand side, e.g. a Variable.
    @attribute rhs      Expression defining the right hand side.
    Grammar:
        odeEquation : lhs=derivative '=' rhs=expression;
    """
    __lhs = None
    __rhs = None

    def __init__(self, _lhs=None, _rhs=None, _sourcePosition=None):
        """
        Standard constructor.
        :param _lhs: an object of type ASTDerivative
        :type _lhs: ASTDerivative
        :param _rhs: an object of type ASTExpression.
        :type _rhs: ASTExpression
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        """
        assert (_lhs is not None and isinstance(_lhs, ASTDerivative)), \
            '(PyNestML.AST.OdeEquation) No or wrong type of left-hand side derivative handed over!'
        assert (_rhs is not None and isinstance(_rhs, ASTExpression)), \
            '(PyNestML.AST.OdeEquation) No or wrong type of right-hand side expression handed over! '
        super(ASTOdeEquation, self).__init__(_sourcePosition)
        self.__lhs = _lhs
        self.__rhs = _rhs

    @classmethod
    def makeASTOdeEquation(cls, _lhs=None, _rhs=None, _sourcePosition=None):
        """
        A factory method used to generate new ASTOdeEquation.
        :param _lhs: an object of type ASTDerivative
        :type _lhs: ASTDerivative
        :param _rhs: an object of type ASTExpression
        :type _rhs: ASTExpression
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        :return a new ASTOdeEquation object.
        :rtype ASTOdeEquation
        """
        return cls(_lhs, _rhs, _sourcePosition)

    def getLhs(self):
        """
        Returns the left-hand side of the equation.
        :return: an object of the ast-derivative class.
        :rtype: ASTDerivative
        """
        return self.__lhs

    def getRhs(self):
        """
        Returns the left-hand side of the equation.
        :return: an object of the ast-expr class.
        :rtype: ASTExpression
        """
        return self.__rhs

    def printAST(self):
        """
        Returns a string representation of the equation.
        :return: a string representing the equation.
        :rtype: str
        """
        return self.getLhs().printAST() + '=' + self.getRhs().printAST()
