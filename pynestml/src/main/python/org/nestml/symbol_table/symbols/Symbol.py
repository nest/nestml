#
# Symbol.py
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
from abc import ABCMeta, abstractmethod


class Symbol:
    """
    This abstract class represents a super-class for all concrete symbols as stored in a symbol table.
    """
    __metaclass__ = ABCMeta
    __elementReference = None
    __scope = None
    __name = None

    def __init__(self, _elementReference=None, _scope=None, _name=None):
        """
        Standard constructor of the Symbol class.
        :param _elementReference: an ast object.
        :type _elementReference: ASTObject
        :param _scope: the scope in which this element is embedded in.
        :type _scope: Scope
        :param _name: the name of the corresponding element
        :type _name: str
        """
        from pynestml.src.main.python.org.nestml.symbol_table.Scope import Scope
        assert (_elementReference is not None), '(PyNestML.SymbolTable.Symbol) No AST reference provided!'
        assert (_scope is not None and isinstance(_scope, Scope)), \
            '(PyNestML.SymbolTable.Symbol) No or wrong type of scope provided!'
        assert (_name is not None and isinstance(_name, str)), \
            '(PyNestML.SymbolTable.Symbol) No or wrong type of symbol-name provided!'
        self.__elementReference = _elementReference
        self.__scope = _scope
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

    def getSymbolName(self):
        """
        Returns the name of this symbol.
        :return: the name of the symbol.
        :rtype: str
        """
        return self.__name

    def isDefinedBefore(self, _sourcePosition=None):
        """
        For a handed over source position, this method checks if this symbol has been defined before the handed
        over position.
        :param _sourcePosition: the position of a different element.
        :type _sourcePosition: ASTSourcePosition
        :return: True, if defined before or at the sourcePosition, otherwise False.
        :rtype: bool
        """
        from pynestml.src.main.python.org.nestml.ast.ASTSourcePosition import ASTSourcePosition
        assert (_sourcePosition is not None and isinstance(_sourcePosition, ASTSourcePosition)), \
            '(PyNestML.SymbolTable.Symbol) No or wrong type of position object handed over!'
        return self.getReferencedObject().getSourcePosition().before(_sourcePosition)

    @abstractmethod
    def printSymbol(self):
        """
        Returns a string representation of this symbol object. This class has to be specified in the corresponding
        sub-class.
        :return: a string representation
        :rtype: str
        """
        pass

    @abstractmethod
    def equals(self, _other=None):
        """
        Checks if the handed over object is equal to this (value-wise).
        :param _other: a symbol object.
        :type _other: Symbol or subclass.
        :return: True if equal, otherwise False.
        :rtype: bool
        """
        pass
