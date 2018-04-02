#
# Scope.py
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

from enum import Enum
from pynestml.modelprocessor.Symbol import Symbol
from pynestml.modelprocessor.ASTSourcePosition import ASTSourcePosition
from pynestml.modelprocessor.Symbol import SymbolKind


class Scope(object):
    """
    This class is used to store a single scope, i.e., a set of elements as declared in this scope directly and 
    a set of sub-scopes with additional elements.
    Attributes:
        __enclosingScope The scope this scope is enclosed in. Type: Scope
        __declaredElements Elements declared in this scope, i.e., scopes and symbols. Type: list(Scope,Symbol)
        __scopeType The type of this scope. Type: ScopeType
        sourcePosition The position in the source file this scope spans over.
    """
    __enclosingScope = None
    __declaredElements = None
    __scopeType = None
    __sourcePosition = None

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
        assert (_scopeType is not None and isinstance(_scopeType, ScopeType)), \
            '(PyNestML.SymbolTable.Scope) No or wrong type of scope type provided (%s)!' % type(_scopeType)
        assert (_enclosingScope is None or isinstance(_enclosingScope, Scope)), \
            '(PyNestML.SymbolTable.Scope) No or wrong type of scope provided (%s)!' % type(_enclosingScope)
        assert (isinstance(_sourcePosition, ASTSourcePosition)), \
            '(PyNestML.SymbolTable.Scope) No or wrong type of source position (%s)!' % type(_sourcePosition)
        self.__declaredElements = list()
        self.__scopeType = _scopeType
        self.__enclosingScope = _enclosingScope
        self.__sourcePosition = _sourcePosition
        return

    def addSymbol(self, _symbol=None):
        """
        Adds the handed over symbol to the current scope.
        :param _symbol: a single symbol object.
        :type _symbol: Symbol
        """
        assert (_symbol is not None and isinstance(_symbol, Symbol)), \
            '(PyNestML.SymbolTable.Scope) No or wrong type of symbol provided (%s)!' % type(_symbol)
        self.__declaredElements.append(_symbol)
        return

    def addScope(self, _scope=None):
        """
        Adds the handed over scope as a sub-scope to the current one.
        :param _scope: a single scope object.
        :type _scope: Scope
        """
        assert (_scope is not None and isinstance(_scope, Scope)), \
            '(PyNestML.SymbolTable.Scope) No or wrong type of scope provided (%s)!' % type(_scope)
        self.__declaredElements.append(_scope)
        return

    def deleteSymbol(self, _symbol=None):
        """
        Used to delete a single symbol from the current scope.
        :param _symbol: a single symbol object.
        :type _symbol: Symbol
        :return: True, if the element has been deleted, otherwise False.
        :rtype: bool
        """
        assert (_symbol is not None and isinstance(_symbol, Symbol)), \
            '(PyNestML.SymbolTable.Scope) No or wrong type of symbol provided (%s)!' % type(_symbol)
        if _symbol in self.__declaredElements:
            self.__declaredElements.remove(_symbol)
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
        assert (_scope is not None and isinstance(_scope, Scope)), \
            '(PyNestML.SymbolTable.Scope) No or wrong type of scope provided (%s)!' % type(_scope)
        if _scope in self.__declaredElements:
            self.__declaredElements.remove(_scope)
            return True
        else:
            return False

    def getSymbolsInThisScope(self):
        """
        Returns the set of elements as defined in this scope, but not in the corresponding super scope.
        :return: a list of symbols defined only in this scope, but not in the upper scopes.
        :rtype: list
        """
        ret = list()
        for elem in self.__declaredElements:
            if isinstance(elem, Symbol):
                ret.append(elem)
        return ret

    def getSymbolsInCompleteScope(self):
        """
        Returns the set of elements as defined in this scope as well as all scopes enclosing this scope.
        :return: a list of symbols defined in this and all enclosing scopes.
        :rtype: list
        """
        symbols = list()
        if self.__enclosingScope is not None:
            symbols.extend(self.__enclosingScope.getSymbolsInThisScope())
        symbols.extend(self.getSymbolsInThisScope())
        return symbols

    def getScopes(self):
        """
        Returns the set of scopes as defined in this scope.
        :return: a list of scope objects
        :rtype: list
        """
        ret = list()
        for elem in self.__declaredElements:
            if isinstance(elem, Scope):
                ret.append(elem)
        return ret

    def resolveToAllScopes(self, _name=None, _type=None):
        """
        Resolves the handed over name and type and returns the scope in which the corresponding symbol has been defined.
        If element has been defined in several scopes, all scopes are returned as a list.
        :param _name: the name of the element.
        :type _name: str
        :param _type: the type of the element
        :type _type: SymbolKind
        :return: the scope in which the element has been defined in
        :rtype: Scope
        """
        assert (_name is not None and isinstance(_name, str)), \
            '(PyNestML.SymbolTable.Scope) No or wrong type of name provided (%s)!' % type(_name)
        assert (_type is not None and isinstance(_type, SymbolKind)), \
            '(PyNestML.SymbolTable.Scope) No or wrong type of symbol-kind provided (%s)!' % type(_type)
        gScope = self.getGlobalScope()
        scopes = gScope.__resolveToScopeInSpannedScope(_name, _type)
        # the following step is done in order to return, whenever the list contains only one element, only this element
        if isinstance(scopes, list) and len(scopes) == 1:
            return scopes[0]
        elif isinstance(scopes, list) and len(scopes) == 0:
            return None
        else:
            return scopes

    def __resolveToScopeInSpannedScope(self, _name=None, _type=None):
        """
        Private method: returns this scope or one of the sub-scopes in which the handed over symbol is defined in.
        :param _name: the name of the element.
        :type _name: str
        :param _type: the type of the element
        :type _type: SymbolKind
        :return: the corresponding scope object.
        :rtype: Scope
        """
        assert (_name is not None and isinstance(_name, str)), \
            '(PyNestML.SymbolTable.Scope) No or wrong type of name provided (%s)!' % type(_name)
        assert (_name is not None and isinstance(_type, SymbolKind)), \
            '(PyNestML.SymbolTable.Scope) No or wrong type of symbol-kind provided (%s)!' % type(_type)
        ret = list()
        for sim in self.getSymbolsInThisScope():
            if sim.get_symbol_name() == _name and sim.get_symbol_kind() == _type:
                ret.append(self)
        for elem in self.getScopes():  # otherwise check if it is in one of the sub-scopes
            temp = elem.__resolveToScopeInSpannedScope(_name, _type)
            if temp is not None:
                ret.extend(temp)
        return ret

    def resolveToAllSymbols(self, _name=None, _type=None):
        """
        Resolves the name and type and returns the corresponding symbol. Caution: Here, we also take redeclaration into
        account. This has to be prevented - if required - by cocos.
        If element has been defined in several scopes, all scopes are returned as a list.
        :param _name: the name of the element.
        :type _name: str
        :param _type: the type of the element
        :type _type: SymbolType
        :return: a single symbol element.
        :rtype: Symbol/list(Symbols)
        """
        assert (_name is not None and isinstance(_name, str)), \
            '(PyNestML.SymbolTable.Scope) No or wrong type of name provided (%s)!' % type(_name)
        assert (_name is not None and isinstance(_type, SymbolKind)), \
            '(PyNestML.SymbolTable.Scope) No or wrong type of symbol-kind provided (%s)!' % type(_type)
        gScope = self.getGlobalScope()
        symbols = gScope.__resolveToSymbolInSpannedScope(_name, _type)
        # the following step is done in order to return, whenever the list contains only one element, only this element
        if isinstance(symbols, list) and len(symbols) == 1:
            return symbols[0]
        elif len(symbols) == 0:
            return None
        else:
            return symbols

    def __resolveToSymbolInSpannedScope(self, _name=None, _type=None):
        """
        Private method: returns a symbol if the handed over name and type belong to a symbol in this or one of the
        sub-scope. Caution: Here, we also take redeclaration into account. This has to be prevented - if required -
        by cocos.
        :param _name: the name of the element.
        :type _name: str
        :param _type: the type of the element
        :type _type: SymbolType
        :return: the corresponding symbol object.
        :rtype: list(Symbol)
        """
        assert (_name is not None and isinstance(_name, str)), \
            '(PyNestML.SymbolTable.Scope) No or wrong type of name provided (%s)!' % type(_name)
        assert (_type is not None and isinstance(_type, SymbolKind)), \
            '(PyNestML.SymbolTable.Scope) No or wrong type of symbol-kind provided (%s)!' % type(_type)
        ret = list()
        for sim in self.getSymbolsInThisScope():
            if sim.get_symbol_name() == _name and sim.get_symbol_kind() == _type:
                ret.append(sim)
        for elem in self.getScopes():  # otherwise check if it is in one of the sub-scopes
            temp = elem.__resolveToSymbolInSpannedScope(_name, _type)
            if temp is not None:
                ret.extend(temp)
        return ret

    def resolveToScope(self, _name=None, _type=None):
        """
        Returns the first scope (starting from this) in which the handed over symbol has been defined, i.e., starting
        from this, climbs recursively upwards unit the element has been located or no enclosing scope is left.
        :param _name: the name of the symbol. 
        :type _name: str
        :param _type: the type of the symbol, i.e., Variable,function or type.
        :type _type: SymbolType
        :return: the first matching scope.
        :rtype: Scope.
        """
        assert (_name is not None and isinstance(_name, str)), \
            '(PyNestML.SymbolTable.Scope) No or wrong type of name provided (%s)!' % type(_name)
        assert (_type is not None and isinstance(_type, SymbolKind)), \
            '(PyNestML.SymbolTable.Scope) No or wrong type of symbol-kind provided (%s)!' % type(_type)
        for sim in self.getSymbolsInThisScope():
            if sim.get_symbol_name() == _name and sim.get_symbol_kind() == _type:
                return self
        if self.hasEnclosingScope():
            return self.getEnclosingScope().resolveToSymbol(_name, _type)
        else:
            return None

    def resolveToSymbol(self, _name=None, _type=None):
        """
        Returns the first symbol corresponding to the handed over parameters, starting from this scope. Starting
        from this, climbs recursively upwards until the element has been located or no enclosing scope is left.
        :param _name: the name of the symbol. 
        :type _name: str
        :param _type: the type of the symbol, i.e., Variable,function or type.
        :type _type: SymbolType
        :return: the first matching symbol.
        :rtype: VariableSymbol or FunctionSymbol
        """
        assert (_name is not None and isinstance(_name, str)), \
            '(PyNestML.SymbolTable.Scope) No or wrong type of name provided (%s)!' % type(_name)
        assert (_type is not None and isinstance(_type, SymbolKind)), \
            '(PyNestML.SymbolTable.Scope) No or wrong type of symbol-kind provided (%s)!' % type(_type)
        for sim in self.getSymbolsInThisScope():
            if sim.get_symbol_name() == _name and sim.get_symbol_kind() == _type:
                return sim
        if self.hasEnclosingScope():
            return self.getEnclosingScope().resolveToSymbol(_name, _type)
        else:
            return None

    def getGlobalScope(self):
        """
        Returns the GLOBAL scope in which all sub-scopes are embedded in.
        :return: the global scope element.
        :rtype: Scope
        """
        if self.getScopeType() is ScopeType.GLOBAL:
            return self
        elif self.hasEnclosingScope():
            return self.getEnclosingScope().getGlobalScope()
        else:
            return None

    def getEnclosingScope(self):
        """
        Returns the enclosing scope if any is defined.
        :return: a scope symbol if available.
        :rtype: Scope
        """
        if self.__enclosingScope is not None:
            return self.__enclosingScope
        else:
            return None

    def hasEnclosingScope(self):
        """
        Returns this scope is embedded in a different scope.
        :return: True, if enclosed, otherwise False.
        :rtype: bool
        """
        return (self.__enclosingScope is not None) and (self.__scopeType is not ScopeType.GLOBAL)

    def getSourcePosition(self):
        """
        Returns the position in the source as enclosed by this scope
        :return: 
        :rtype: 
        """
        return self.__sourcePosition

    def getScopeType(self):
        """
        Returns the type of scope.
        :return: a ScopeType element.
        :rtype: ScopeType
        """
        return self.__scopeType

    def isEnclosedIn(self, _scope=None):
        """
        Returns if this scope is directly or indirectly enclosed in the handed over scope.
        :param _scope: the scope in which this scope can be enclosed in.
        :type _scope Scope
        :return: True, if this scope is directly or indirectly enclosed in the handed over one, otherwise False.
        :rtype: bool
        """
        assert (_scope is not None and isinstance(_scope, Scope)), \
            '(PyNestML.SymbolTable.Scope) No or wrong type of scope provided (%s)!' % type(_scope)
        if self.hasEnclosingScope() and self.getEnclosingScope() is _scope:
            return True
        elif self.hasEnclosingScope():
            return self.getEnclosingScope().isEnclosedIn(_scope)
        else:
            return False

    def getDepthOfScope(self):
        """
        Returns the depth of this scope.
        :return: the level of encapsulation of this scope.
        :rtype: int
        """
        depth = 0
        if self.hasEnclosingScope():
            depth += 1 + self.getEnclosingScope().getDepthOfScope()
        return depth

    def printScope(self):
        """
        Returns a string representation of symbol table as used for debug purpose.
        :return: a string representation of the scope and its sub-scope.
        :rtype: str
        """
        ret = ('-' * 2 * (self.getDepthOfScope())) + '<' + self.getScopeType().name \
              + ',' + str(self.getSourcePosition()) + '>' + '\n'
        for elem in self.__declaredElements:
            if isinstance(elem, Symbol):
                ret += ('-' * 2 * (self.getDepthOfScope() + 1)) + elem.print_symbol() + '\n'
            else:
                ret += elem.printScope()
        return ret


class ScopeType(Enum):
    """
    This enum is used to distinguish between different types of scopes, namely:
        -The global scope (neuron), in which all the sub-scopes are embedded.
        -The function scope, as embedded in the global scope.
        -The update scope, as embedded in the global scope.
    """
    GLOBAL = 1
    UPDATE = 2
    FUNCTION = 3
