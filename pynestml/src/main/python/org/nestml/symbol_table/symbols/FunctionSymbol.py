#
# FunctionSymbol.py
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
# along with NEST.  If not, see <http://www.gnu.org/licenses/>.#
from pynestml.src.main.python.org.nestml.symbol_table.symbols.TypeSymbol import TypeSymbol
from pynestml.src.main.python.org.nestml.symbol_table.symbols.Symbol import Symbol


class FunctionSymbol(Symbol):
    """
    This class is used to store a single function symbol, e.g. the definition of the function max.
    """
    __paramTypes = None
    __returnType = None
    __isPredefined = False

    def __init__(self, _name=None, _paramTypes=list(), _returnType=None, _elementReference=None, _scope=None,
                 _isPredefined=False):
        """
        Standard constructor.
        :param _name: the name of the function symbol.
        :type _name: str
        :param _paramTypes: a list of argument types.
        :type _paramTypes: list(TypeSymbol)
        :param _returnType: the return type of the function.
        :type _returnType: TypeSymbol
        :param _elementReference: a reference to the ASTFunction which corresponds to this symbol (if not predefined)
        :type _elementReference: ASTFunction
        :param _scope: a reference to the scope in which this symbol is defined in
        :type _scope: Scope
        :param _isPredefined: True, if this element is a predefined one, otherwise False.
        :type _isPredefined: bool
        """
        super(FunctionSymbol, self).__init__(_elementReference=_elementReference, _scope=_scope, _name=_name)
        assert (_returnType is not None and isinstance(_returnType, TypeSymbol)), \
            '(PyNestML.SymbolTable.FunctionSymbol) No or wrong type of type symbol provided!'
        for arg in _paramTypes:
            assert (arg is not None and isinstance(arg, TypeSymbol)), \
                '(PyNestML.SymbolTable.FunctionSymbol) No or wrong type of argument provided!'
        assert (_isPredefined is not None and isinstance(_isPredefined, bool)), \
            'PyNestML.SymbolTable.FunctionSymbol) No or wrong type of predefined-specification provided!'
        self.__paramTypes = _paramTypes
        self.__returnType = _returnType
        self.__isPredefined = _isPredefined

    def printSymbol(self):
        ret = 'MethodSymbol[' + super(Symbol).getSymbolName() + ', Parameters = '
        for arg in self.__paramTypes:
            ret += arg.printSymbol()
            if arg < len(self.__paramTypes) - 1:  # in the case that it is not the last arg, print also a comma
                ret += ','
        return ret + ']'

    def getReturnType(self):
        """
        Returns the return type of this function symbol
        :return: a single type symbol.
        :rtype: TypeSymbol
        """
        return self.__returnType

    def setReturnType(self, _newType=None):
        """
        Sets the return type to the handed over one.
        :param _newType: a single type symbol
        :type _newType: TypeSymbol
        """
        assert (_newType is not None and isinstance(_newType, TypeSymbol)), \
            '(PyNestML.SymbolTable.FunctionSymbol) No or wrong type of type symbol provided!'
        self.__returnType = _newType

    def getParameterTypes(self):
        """
        Returns a list of all parameter types.
        :return: a list of parameter types.
        :rtype: list(TypeSymbol)
        """
        return self.__paramTypes

    def addParameterType(self, _newType=None):
        """
        Adds the handed over type to the list of argument types.
        :param _newType: a single type symbol
        :type _newType: TypeSymbol
        """
        assert (_newType is not None and isinstance(_newType, TypeSymbol)), \
            '(PyNestML.SymbolTable.FunctionSymbol) No or wrong type of type symbol provided!'
        self.__paramTypes.append(_newType)

    def isPredefined(self):
        """
        Returns whether it is a predefined function or not.
        :return: True if predefined, otherwise False
        :rtype: bool
        """
        return self.__isPredefined

    def equals(self, _other=None):
        """
        Compares the handed over instance of function symbol to this one and returns true, if the they are equal.
        :param _other: a different function symbol
        :type _other: FunctionSymbol
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if type(_other) != type(self) or self.__name != _other.getSymbolName() \
                or not self.__returnType.equals() or len(self.__paramTypes) != len(_other.getParameterTypes()):
            return False
        otherArgs = _other.getParameterTypes()
        for i in range(0, len(self.__paramTypes)):
            if not self.__paramTypes[i].equals(otherArgs[i]):
                return False
        return True
