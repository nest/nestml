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
from copy import copy

from pynestml.modelprocessor.ASTElement import ASTElement
from pynestml.modelprocessor.Either import Either


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
        assert (_differentialOrder is not None and isinstance(_differentialOrder, int)), \
            '(PyNestML.AST.Variable) No or wrong type of differential order provided (%s)!' % type(_differentialOrder)
        assert (_differentialOrder >= 0), \
            '(PyNestML.AST.Variable) Differential order must be at least 0, is %d!' % _differentialOrder
        assert (_name is not None and isinstance(_name, str)), \
            '(PyNestML.AST.Variable) No or wrong type of name provided (%s)!' % type(_name)
        super(ASTVariable, self).__init__(_sourcePosition=_sourcePosition)
        self.__name = _name
        self.__differentialOrder = _differentialOrder
        return

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

    def resolveInOwnScope(self):
        from pynestml.modelprocessor.Symbol import SymbolKind
        assert self.getScope() is not None

        return self.getScope().resolveToSymbol(self.getCompleteName(), SymbolKind.VARIABLE)

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

    def getCompleteName(self):
        """
        Returns the complete name, consisting of the name and the differential order.
        :return: the complete name.
        :rtype: str
        """
        return self.getName() + '\'' * self.getDifferentialOrder()

    def getNameOfLhs(self):
        """
        Returns the complete name but with differential order reduced by one.
        :return: the name.
        :rtype: str
        """
        if self.getDifferentialOrder() > 0:
            return self.getName() + '\'' * (self.getDifferentialOrder() - 1)
        else:
            return self.getName()

    def getTypeSymbol(self):
        """
        Returns the type symbol of this expression.
        :return: a single type symbol.
        :rtype: TypeSymbol
        """
        return copy(self.__typeSymbol)

    def setTypeSymbol(self, _typeSymbol=None):
        """
        Updates the current type symbol to the handed over one.
        :param _typeSymbol: a single type symbol object.
        :type _typeSymbol: TypeSymbol
        """
        assert (_typeSymbol is not None and isinstance(_typeSymbol, Either)), \
            '(PyNestML.AST.Variable) No or wrong type of type symbol provided (%s)!' % type(_typeSymbol)
        self.__typeSymbol = _typeSymbol
        return

    def getParent(self, _ast=None):
        """
        Indicates whether a this node contains the handed over node.
        :param _ast: an arbitrary ast node.
        :type _ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        return None

    def isUnitVariable(self):
        """
        Provided on-the-fly information whether this variable represents a unit-variable, e.g., nS.
        Caution: It assumes that the symbol table has already been constructed.
        :return: True if unit-variable, otherwise False.
        :rtype: bool
        """
        from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes
        if self.getName() in PredefinedTypes.getTypes():
            return True
        else:
            return False

    def __str__(self):
        """
        Returns the string representation of the variable.
        :return: the variable as a string.
        :rtype: str
        """
        ret = self.__name
        for i in range(1, self.__differentialOrder + 1):
            ret += "'"
        return ret

    def equals(self, _other=None):
        """
        The equals method.
        :param _other: a different object.
        :type _other: object
        :return: True if equals, otherwise False.
        :rtype: bool
        """
        if not isinstance(_other, ASTVariable):
            return False
        return self.getName() == _other.getName() and self.getDifferentialOrder() == _other.getDifferentialOrder()
