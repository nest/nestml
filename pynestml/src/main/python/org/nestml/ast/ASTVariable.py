#
# ASTVariable.py
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

from pynestml.src.main.python.org.nestml.ast.ASTElement import ASTElement


class ASTVariable(ASTElement):
    """
    This class is used to store a single variable.
    
    ASTVariable Provides a 'marker' AST node to identify variables used in expressions.
    @attribute name
    Grammar:
        variable : NAME (differentialOrder='\'')*;
    """
    __name = None
    __differentialOrder = None
    # the corresponding type symbol
    __typeSymbol = None

    def __init__(self, _name=None, _differentialOrder=0, _sourcePosition=None):
        """
        Standard constructor.
        :param _name: the name of the variable
        :type _name: str
        :param _differentialOrder: the differential order of the variable.
        :type _differentialOrder: int
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        """
        assert (_differentialOrder >= 0), \
            '(PyNestML.AST.Variable) Differential order must be at least 0, is %d' % _differentialOrder
        assert (_name is not None), \
            '(PyNestML.AST.Variable) Name of variable must not be None'
        super(ASTVariable, self).__init__(_sourcePosition)
        self.__name = _name
        self.__differentialOrder = _differentialOrder

    @classmethod
    def makeASTVariable(cls, _name=None, _differentialOrder=0, _sourcePosition=None):
        """
        The factory method of the ASTVariable class.
        :param _name: the name of the variable
        :type _name: str
        :param _differentialOrder: the differential order of the variable.
        :type _differentialOrder: int
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        :return: a new ASTVariable object.
        :rtype: ASTVariable
        """
        return cls(_name, _differentialOrder, _sourcePosition)

    def getName(self):
        """
        Returns the name of the variable.
        :return: the name of the variable.
        :rtype: str
        """
        return self.__name

    def getDifferentialOrder(self):
        """
        Returns the differential order of the variable.
        :return: the differential order.
        :rtype: int
        """
        return self.__differentialOrder

    def getTypeSymbol(self):
        """
        Returns the type symbol of this expression.
        :return: a single type symbol.
        :rtype: TypeSymbol
        """
        return self.__typeSymbol

    def setTypeSymbol(self, _typeSymbol=None):
        """
        Updates the current type symbol to the handed over one.
        :param _typeSymbol: a single type symbol object.
        :type _typeSymbol: TypeSymbol
        """
        from pynestml.src.main.python.org.nestml.symbol_table.symbols.TypeSymbol import TypeSymbol
        assert (_typeSymbol is not None and isinstance(_typeSymbol, TypeSymbol)), \
            '(PyNestML.AST.Expression) No or wrong type of type symbol provided (%s)!' % type(_typeSymbol)
        self.__typeSymbol = _typeSymbol

    def printAST(self):
        """
        Returns the string representation of the variable.
        :return: the variable as a string.
        :rtype: str
        """
        ret = self.__name
        for i in range(1, self.__differentialOrder + 1):
            ret += "'"
        return ret
