"""
/*
 *  ASTParameter.py
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
from pynestml.src.main.python.org.nestml.ast.ASTDatatype import ASTDatatype


class ASTParameter(ASTElement):
    """
    This class is used to store a single function parameter definition.
    ASTParameter represents singe:
      output: spike
    @attribute compartments Lists with compartments.
    Grammar:
        parameter : NAME datatype;
    """
    __name = None
    __dataType = None

    def __init__(self, _name=None, _dataType=None, _sourcePosition=None):
        """
        Standard constructor.
        :param _name: the name of the parameter.
        :type _name: str
        :param _dataType: the type of the parameter. 
        :type _dataType: ASTDatatype
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        """
        assert (_name is not None and isinstance(_name, str)), \
            '(PyNestML.AST.Parameter) No or wrong type of name provided!'
        assert (_dataType is not None and isinstance(_dataType, ASTDatatype)), \
            '(PyNestML.AST.Parameter) No or wrong type of datatype provided!'
        super(ASTParameter, self).__init__(_sourcePosition)
        self.__dataType = _dataType
        self.__name = _name

    @classmethod
    def makeASTParameter(cls, _name=None, _dataType=None, _sourcePosition=None):
        """
        The factory method of the ASTParameter class.
        :param _name: the name of the parameter.
        :type _name: str
        :param _dataType: the type of the parameter. 
        :type _dataType: ASTDatatype
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        :return: a new ASTParameter object.
        :rtype: ASTParameter
        """
        return cls(_name, _dataType)

    def getName(self):
        """
        Returns the name of the parameter.
        :return: the name of the parameter.
        :rtype: str
        """
        return self.__name

    def getDataType(self):
        """
        Returns the data type of the parameter.
        :return: the data type of the parameter.
        :rtype: ASTDataType
        """
        return self.__dataType

    def printAST(self):
        """
        Returns a string representation of the parameter.
        :return: a string representation.
        :rtype: str
        """
        return self.getName() + ' ' + self.getDataType().printAST()
