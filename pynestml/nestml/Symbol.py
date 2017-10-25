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
from enum import Enum


class Symbol(object):
    """
    This abstract class represents a super-class for all concrete symbols as stored in a symbol table.
    """
    __metaclass__ = ABCMeta
    __elementReference = None
    __scope = None
    __name = None
    __symbolKind = None
    __comment = None

    def __init__(self, _elementReference=None, _scope=None, _name=None, _symbolKind=None):
        """
        Standard constructor of the Symbol class.
        :param _elementReference: an ast object.
        :type _elementReference: ASTObject
        :param _scope: the scope in which this element is embedded in.
        :type _scope: Scope
        :param _name: the name of the corresponding element
        :type _name: str
        :type _symbolKind:
        """
        from pynestml.nestml.Scope import Scope
        assert (_scope is None or isinstance(_scope, Scope)), \
            '(PyNestML.SymbolTable.Symbol) Wrong type of scope provided (%s)!' % type(_scope)
        assert (_name is not None and isinstance(_name, str)), \
            '(PyNestML.SymbolTable.Symbol) No or wrong type of name provided (%s)!' % type(_name)
        assert (_symbolKind is not None and isinstance(_symbolKind, SymbolKind)), \
            '(PyNestML.SymbolTable.Symbol) No or wrong type of symbol-type provided (%s)!' % type(_symbolKind)
        self.__elementReference = _elementReference
        self.__scope = _scope
        self.__name = _name
        self.__symbolKind = _symbolKind
        return

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

    def getSymbolKind(self):
        """
        Returns the type of this symbol.
        :return: the type of this symbol.
        :rtype: SymbolKind
        """
        return self.__symbolKind

    def isDefinedBefore(self, _sourcePosition=None):
        """
        For a handed over source position, this method checks if this symbol has been defined before the handed
        over position.
        :param _sourcePosition: the position of a different element.
        :type _sourcePosition: ASTSourcePosition
        :return: True, if defined before or at the sourcePosition, otherwise False.
        :rtype: bool
        """
        from pynestml.nestml.ASTSourcePosition import ASTSourcePosition
        assert (_sourcePosition is not None and isinstance(_sourcePosition, ASTSourcePosition)), \
            '(PyNestML.SymbolTable.Symbol) No or wrong type of position object provided (%s)!' % type(_sourcePosition)
        return self.getReferencedObject().getSourcePosition().before(_sourcePosition)

    def hasComment(self):
        return self.__comment is not None

    def getComment(self):
        return self.__comment

    def setComment(self, _comment=None):
        self.__comment = _comment

    @abstractmethod
    def printSymbol(self):
        """
        Returns a string representation of this symbol.
        """
        pass


class SymbolKind(Enum):
    """
    An enumeration of all possible symbol types to make processing easier.
    """
    VARIABLE = 1
    TYPE = 2
    FUNCTION = 3
