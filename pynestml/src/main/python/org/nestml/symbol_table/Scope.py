"""
/*
 *  Scope.py
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
from pynestml.src.main.python.org.nestml.symbol_table.Symbol import Symbol
from pynestml.src.main.python.org.nestml.ast.ASTSourcePosition import ASTSourcePosition


class Scope:
    """
    This class is used to store a single scope, i.e., a set of elements as declared in this scope directly and 
    a set of sub-scopes with additional elements.
    """
    __enclosing_scope = None
    __declared_symbols = None
    __declared_scopes = None
    __scope_type = None
    __source_position = None

    def __init__(self, _scopeType=None, _enclosingScope=None, _sourcePosition=None):
        """
        Standard constructor as used to create a new scope.
        :param _scopeType: the type of this scope
        :type _scopeType: ScopeType
        :param _enclosingScope: the parent scope of this scope, as used for resolution of symbols.
        :type _enclosingScope: Scope
        :param _sourcePosition: the start and end of the scope in the source file
        :type _sourcePosition: SourcePosition
        """
        assert (isinstance(_scopeType, ScopeType)), '(PyNestML.SymbolTable.Scope) Type of scope not defined!'
        assert (isinstance(_enclosingScope, Scope)), '(PyNestML.SymbolTable.Scope) Not a scope object handed over!'
        assert (isinstance(_sourcePosition, ASTSourcePosition)), \
            '(PyNestML.SymbolTable.Scope) No source position handed over!'
        self.__declared_scopes = list()
        self.__declared_symbols = list()
        self.__scope_type = _scopeType
        self.__enclosing_scope = _enclosingScope

    def addSymbolToScope(self, _symbol=None):
        """
        Adds the handed over symbol to the current scope.
        :param _symbol: a single symbol object.
        :type _symbol: Symbol
        :return: no value returned
        :rtype: void
        """
        assert (isinstance(_symbol, Symbol)), \
            '(PyNestML.SymbolTable.Scope) Non-symbol object can not be added to the scope!'
        self.__declared_symbols.append(_symbol)

    def addScopeToScope(self, _scope=None):
        """
        Adds the handed over scope as a sub-scope to the current one.
        :param _scope: a single scope object.
        :type _scope: Scope
        :return: 
        :rtype: 
        """
        assert (isinstance(_scope, Scope)), \
            '(PyNestML.SymbolTable.Scope) Non-scope object can not be added to the scope!'
        self.__declared_scopes.append(_scope)

    def deleteSymbol(self, _symbol=None):
        """
        Used to delete a single symbol from the current scope.
        :param _symbol: a single symbol object.
        :type _symbol: Symbol
        :return: True, if the element has been deleted, otherwise False.
        :rtype: bool
        """
        assert (isinstance(_symbol, Symbol)), \
            '(PyNestML.SymbolTable.Scope) Non-symbol object can not be deleted from the scope!'
        if _symbol in self.__declared_symbols:
            self.__declared_scopes.remove(_symbol)
            return True
        else:
            return False

    def deleteScope(self, _scope=None):
        """
        Used to delete a single sub-scope from the current scope.
        :param _scope: a single scope object.
        :type _scope: Scope
        :return: True, if the element has been deleted, otherwise False.
        :rtype: bool
        """
        assert (isinstance(_scope, Scope)), \
            '(PyNestML.SymbolTable.Scope) Non-scope object can not be deleted from the scope.'
        if _scope in self.__declared_scopes:
            self.__declared_scopes.remove(_scope)
            return True
        else:
            return False

    def getSymbolsInCurrentScope(self):
        """
        Returns the set of elements as defined in this scope, but not in the corresponding super scope.
        :return: a list of symbols defined only in this scope, but not in the upper scopes.
        :rtype: list
        """
        return self.__declared_symbols

    def getSymbolsInCompleteScope(self):
        """
        Returns the set of elements as defined in this scope as well as all scopes enclosing this scope.
        :return: a list of symbols defined in this and all enclosing scopes.
        :rtype: list
        """
        symbols = list()
        if self.__enclosing_scope is not None:
            symbols.append(self.__enclosing_scope.getSymbols())
        symbols.append(self.__declared_symbols)
        return symbols

    def getScopes(self):
        """
        Returns the set of scopes as defined in this scope.
        :return: a list of scope objects
        :rtype: list
        """
        return self.__declared_scopes

    def resolveSymbol(self, _symbol=None):
        """
        Returns the scope of the handed over symbol.
        :return: the corresponding scope object.
        :rtype: Scope
        """
        assert (isinstance(_symbol, Symbol)), '(PyNestML.SymbolTable.Scope) Not a symbol object!'
        if _symbol in self.__declared_symbols:
            return self
        elif self.hasEnclosingScope():
            return self.getEnclosingScope().resolveSymbol(_symbol)
        else:
            return None

    def getEnclosingScope(self):
        """
        Returns the enclosing scope if any is defined.
        :return: a scope symbol if available.
        :rtype: Scope
        """
        if self.__enclosing_scope is not None:
            return self.__enclosing_scope
        else:
            return None

    def hasEnclosingScope(self):
        """
        Returns this scope is embedded in a different scope.
        :return: True, if enclosed, otherwise False.
        :rtype: bool
        """
        return (self.__enclosing_scope is not None) and (self.__scope_type is not ScopeType.GLOBAL)

    def getSourcePosition(self):
        """
        Returns the position in the source as enclosed by this scope
        :return: 
        :rtype: 
        """
        return self.__source_position

    def getScopeType(self):
        """
        Returns the type of scope.
        :return: a ScopeType element.
        :rtype: ScopeType
        """
        return self.__scope_type


class ScopeType(Enum):
    """
    This enum is used to distinguish between different types of scopes, namely:
        -The global scope, in which all the sub-scopes are embedded.
        -The function scope, as embedded in the global scope.
        -The update scope, as embedded in the global scope.
        -The local scope, as embedded in the update or function scope (e.g. if branches etc.).
    """
    GLOBAL = 1
    UPDATE = 2
    FUNCTION = 3
    LOCAL = 4
