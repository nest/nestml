"""
/*
 *  ASTParameters.py
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


class ASTParameters:
    """
    This class is used to store a set of parameters.
    ASTParameters models parameter list in function declaration.
    @attribute parameters List with parameters.
    Grammar:
        parameters : parameter (',' parameter)*;
    """
    __parameterList = None

    def __init__(self, _parameterList=list()):
        """
        Standard constructor.
        :param _parameterList: a list of parameter objects. 
        :type _parameterList: list(ASTParameter)
        """
        self.__parameterList = _parameterList

    @classmethod
    def makeASTParameters(cls, _parameterList=list()):
        """
        Factory method of the ASTParameters class.
        :param _parameterList: a list of parameter objects. 
        :type _parameterList: list(ASTParameter)
        :return: a new ASTParameters object.
        :rtype: ASTParameters
        """

    def getParametersList(self):
        """
        Returns the list of parameters.
        :return: a list of parameter objects.
        :rtype: list(ASTParameter)
        """
        return self.__parameterList

    def printAST(self):
        """
        Returns a string representation of the parameters.
        :return: a string representation.
        :rtype: str
        """
        ret = ''
        if self.getParametersList() is not None:
            for par in self.getParametersList():
                ret += par.printAST() + '\n'
        return ret
