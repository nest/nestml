"""
/*
 *  Symbol.py
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
from enum import Enum


class Symbol:
    """
    This class is ues to store information regarding a single symbol as required for a correct handling of scopes
    and context conditions. A single symbol is a declaration or an argument of a function.
    E.g.:   V_m mV = .... 
            function x(arg1,...)
    """
    __elementReference = None
    __scope = None
    __type = None
    __name = None

    def __init__(self, _elementReference=None, _scope=None, _type=None, _name=None):
        """
        Standard constructor of the Symbol class.
        :param _elementReference: an ast object.
        :type _elementReference: ASTObject
        :param _scope: the scope in which this element is embedded in.
        :type _scope: Scope
        :param _type: the type of this symbol, i.e., VARIABLE or FUNCTION
        :type _type: SymbolType
        :param _name: the name of the corresponding element
        :type _name: str
        """
        from pynestml.src.main.python.org.nestml.symbol_table.Scope import Scope
        assert (_elementReference is not None), '(PyNestML.SymbolTable.Symbol) No AST reference provided!'
        assert (_scope is not None and isinstance(_scope, Scope)), \
            '(PyNestML.SymbolTable.Symbol) No or wrong type of scope provided!'
        assert (_type is not None and isinstance(_type, SymbolType)), \
            '(PyNestML.SymbolTable.Symbol) Type of symbol not or wrongly specified!'
        assert (_name is not None and isinstance(_name, str)), \
            '(PyNestML.SymbolTable.Symbol) Name of symbol not or wrongly specified!'
        self.__elementReference = _elementReference
        self.__scope = _scope
        self.__type = _type
        self.__name = _name

    def getReferencedObject(self):
        """
        Returns the referenced object.
        :return: the referenced object.
        :rtype: ASTObject
        """
        return self.__elementReference

    def getCorrespondingScope(self):
        """
        Returns the scope in which this symbol is embedded in.
        :return: a scope object.
        :rtype: Scope
        """
        return self.__scope

    def getSymbolType(self):
        """
        Returns the type of this symbol.
        :return: the type of the symbol
        :rtype: SymbolType
        """
        return self.__type

    def getSymbolName(self):
        """
        Returns the name of this symbol.
        :return: the name of the symbol.
        :rtype: str
        """
        return self.__name

    def printSymbol(self):
        """
        Returns a string representation of this symbol object.
        :return: a string representation
        :rtype: str
        """
        if self.getSymbolType() is SymbolType.FUNCTION:
            return '[' + str(self.getSymbolName()) + ',' + 'FUNCTION' \
                   + ',' + self.getReferencedObject().getSourcePosition().printSourcePosition() + ']'
        else:
            return '[' + str(self.getSymbolName()) + ',' + 'VARIABLE' + \
                   ',' + self.getReferencedObject().getSourcePosition().printSourcePosition() + ']'


class SymbolType(Enum):
    """
    This enum is used to represent the type of a function as used to resolve and store symbols.
    """
    VARIABLE = 1
    FUNCTION = 2
