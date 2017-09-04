"""
 /*
 *  ASTDerivative.py
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


class ASTDerivative(ASTElement):
    """
    This class is used to store a derivative, e.g., V_m'.
    Grammar:
        derivative : name=NAME (differentialOrder='\'')*;
    """
    __name = None
    __differentialOrder = None

    def __init__(self, _name=None, _differentialOrder=0, _sourcePosition=None):
        """
        Standard constructor.
        :param _name: the name of the variable.
        :type _name: str
        :param _differentialOrder: the differential order of the variable
        :type _differentialOrder: int 
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        """
        assert (_differentialOrder >= 0), '(PyNestML.AST.Derivative) Negative differential order provided!'
        assert (_name is not None), '(PyNestML.AST.Derivative) No name provided!'
        super(ASTDerivative, self).__init__(_sourcePosition)
        self.__differentialOrder = _differentialOrder
        self.__name = _name

    @classmethod
    def makeASTDerivative(cls, _name=None, _differentialOrder=0, _sourcePosition=None):
        """
         A factory method used to generate new ASTDerivative.
        :param _name: the name of the variable.
        :type _name: str
        :param _differentialOrder: the differential order of the variable
        :type _differentialOrder: int 
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        :return: a new ASTDerivative object.
        :rtype: ASTDerivative
        """
        return cls(_name, _differentialOrder, _sourcePosition)

    def getName(self):
        """
        Returns the name of the derivative.
        :return: the name. 
        :rtype: str
        """
        return self.__name

    def getDifferentialOrder(self):
        """
        Returns the differential order of the derivative.
        :return: the order of the variable.
        :rtype: int
        """
        return self.__differentialOrder

    def printAST(self):
        """
        Returns the string representation of the derivative.
        :return: a string representation.
        :rtype: str
        """
        return self.getName() + '\'' * self.getDifferentialOrder()
