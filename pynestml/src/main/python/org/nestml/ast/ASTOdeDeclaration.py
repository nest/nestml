"""
/*
 *  ASTOdeDeclaration.py
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
from pynestml.src.main.python.org.nestml.ast.ASTEquation import ASTEquation
from pynestml.src.main.python.org.nestml.ast.ASTShape import ASTShape
from pynestml.src.main.python.org.nestml.ast.ASTOdeFunction import ASTOdeFunction


class ASTOdeDeclaration:
    """
    This class is used to store an arbitrary ODE declaration, e.g., a shape.
    Grammar:
        odeDeclaration  : (equation | shape | odeFunction | NEWLINE)+;
    """
    __elements = None

    def __init__(self, _elements=list()):
        """
        Standard constructor.
        :param _elements: a list of elements.
        :type _elements: list(ASTEquation|ASTShape|ASTOdeFunction)
        """
        self.__elements = _elements

    @classmethod
    def makeASTOdeDeclaration(cls, _elements=list()):
        """
        A factory method used to generate new ASTOdeDeclaration.
        :param _elements: a list of elements.
        :type _elements: list(ASTEquation|ASTShape|ASTOdeFunction)
        """
        return cls(_elements)

    def getElements(self):
        """
        Return all ode elements, regardless of the type.
        :return: a list of elements.
        :rtype: list
        """
        return self.__elements

    def getEquations(self):
        """
        Returns the list of stored equation objects.
        :return: a list of ASTEquation objects.
        :rtype: list(ASTEquation)
        """
        ret = list()
        if self.getElements() is not None:
            for el in self.getElements():
                if isinstance(el, ASTEquation):
                    ret.append(el)
        return ret

    def getShapes(self):
        """
        Returns the list of stored shape objects.
        :return: a list of ASTShape objects.
        :rtype: list(ASTShape)
        """
        ret = list()
        if self.getElements() is not None:
            for el in self.getElements():
                if isinstance(el, ASTShape):
                    ret.append(el)
        return ret

    def getOdeFunction(self):
        """
        Returns the list of stored ode function objects.
        :return: a list of ASTShape objects.
        :rtype: list(ASTOdeFunction)
        """
        ret = list()
        if self.getElements() is not None:
            for el in self.getElements():
                if isinstance(el, ASTOdeFunction):
                    ret.append(el)
        return ret

    def printAST(self):
        """
        Returns a string representation of the ode-declaration.
        :return: a string representation
        :rtype: str
        """
        ret = ''
        if self.getElements() is not None:
            for el in self.getElements():
                ret += el.printAST() + '\n'
        return ret
