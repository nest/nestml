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
from pynestml.src.main.python.org.nestml.symbol_table.symbols.Symbol import SymbolType


class FunctionSymbol(Symbol):
    """
    This class is used to store a single function symbol, e.g. the definition of the function max.
    """
    __name = None
    __args = None
    __returnType = None

    def __init__(self, _name=None, _args=list(), _returnType=None, _elementReference=None, _scope=None):
        """
        Standard constructor.
        :param _name: the name of the function symbol.
        :type _name: str
        :param _args: a list of argument types.
        :type _args: list(TypeSymbol)
        :param _returnType: the return type of the function.
        :type _returnType: TypeSymbol
        """
        super(Symbol, self).__init__(_elementReference=_elementReference,
                                     _scope=_scope, _type=SymbolType.FUNCTION, _name=_name)
        assert (_name is not None and isinstance(_returnType, TypeSymbol)), \
            '(PyNestML.SymbolTable.FunctionSymbol) No or wrong type of type symbol provided!'
        for arg in _args:
            assert (arg is not None and isinstance(arg, TypeSymbol)), \
                '(PyNestML.SymbolTable.FunctionSymbol) No or wrong type of argument provided!'
        self.__args = _args
        self.__returnType = _returnType

    def printSymbol(self):
        ret = 'MethodSymbol[' + super(Symbol).getSymbolName() + ', Parameters = '
        for arg in self.__args:
            ret + arg.printSymbol()
            if arg < len(self.__args) - 1:  # in the case that it is not the last arg, print also a comma
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
        return self.__args

    def addParameterType(self, _newType=None):
        """
        Adds the handed over type to the list of argument types.
        :param _newType: a single type symbol
        :type _newType: TypeSymbol
        """
        assert (_newType is not None and isinstance(_newType, TypeSymbol)), \
            '(PyNestML.SymbolTable.FunctionSymbol) No or wrong type of type symbol provided!'
        self.__args.append(_newType)

    def equals(self, _other=None):
        """
        Compares the handed over instance of function symbol to this one and returns true, if the they are equal.
        :param _other: a different function symbol
        :type _other: FunctionSymbol
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        if type(_other) != type(self) or self.__name != _other.getName() \
                or not self.__returnType.equals() or len(self.__args) != len(_other.getParameterTypes()):
            return False
        otherArgs = _other.getParameterTypes()
        for i in range(0, len(self.__args)):
            if not self.__args[i].equals(otherArgs[i]):
                return False
        return True
