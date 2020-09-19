# -*- coding: utf-8 -*-
#
# scope.py
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

from pynestml.symbols.symbol import Symbol, SymbolKind


class Scope(object):
    """
    This class is used to store a single scope, i.e., a set of elements as declared in this scope directly and
    a set of sub-scopes with additional elements.
    Attributes:
        enclosing_scope The scope this scope is enclosed in. Type: Scope
        declared_elements Elements declared in this scope, i.e., scopes and symbols. Type: list(Scope,Symbol)
        scope_type The type of this scope. Type: ScopeType
        source_position The position in the source file this scope spans over.
    """

    def __init__(self, scope_type, enclosing_scope=None, source_position=None):
        """
        Standard constructor as used to create a new scope.
        :param scope_type: the type of this scope
        :type scope_type: ScopeType
        :param enclosing_scope: the parent scope of this scope, as used for resolution of symbols.
        :type enclosing_scope: Scope
        :param source_position: the start and end of the scope in the source file
        :type source_position: ast_source_location
        """
        self.declared_elements = list()
        self.scope_type = scope_type
        self.enclosing_scope = enclosing_scope
        self.source_position = source_position

    def add_symbol(self, symbol):
        """
        Adds the handed over symbol to the current scope.
        :param symbol: a single symbol object.
        :type symbol: Symbol
        """
        self.declared_elements.append(symbol)

    def update_variable_symbol(self, _symbol):
        for symbol in self.get_symbols_in_this_scope():
            if (symbol.get_symbol_kind() == SymbolKind.VARIABLE
                    and symbol.get_symbol_name() == _symbol.get_symbol_name()):
                self.declared_elements.remove(symbol)
                self.add_symbol(_symbol)
                break

    def add_scope(self, scope):
        """
        Adds the handed over scope as a sub-scope to the current one.
        :param scope: a single scope object.
        :type scope: Scope
        """
        self.declared_elements.append(scope)

    def delete_symbol(self, symbol):
        """
        Used to delete a single symbol from the current scope.
        :param symbol: a single symbol object.
        :type symbol: Symbol
        :return: True, if the element has been deleted, otherwise False.
        :rtype: bool
        """
        if symbol in self.declared_elements:
            self.declared_elements.remove(symbol)
            return True
        else:
            return False

    def delete_scope(self, scope):
        """
        Used to delete a single sub-scope from the current scope.
        :param scope: a single scope object.
        :type scope: Scope
        :return: True, if the element has been deleted, otherwise False.
        :rtype: bool
        """
        if scope in self.declared_elements:
            self.declared_elements.remove(scope)
            return True
        else:
            return False

    def get_symbols_in_this_scope(self):
        """
        Returns the set of elements as defined in this scope, but not in the corresponding super scope.
        :return: a list of symbols defined only in this scope, but not in the upper scopes.
        :rtype: list
        """
        ret = list()
        for elem in self.declared_elements:
            if isinstance(elem, Symbol):
                ret.append(elem)
        return ret

    def get_symbols_in_complete_scope(self):
        """
        Returns the set of elements as defined in this scope as well as all scopes enclosing this scope.
        :return: a list of symbols defined in this and all enclosing scopes.
        :rtype: list
        """
        symbols = list()
        if self.enclosing_scope is not None:
            symbols.extend(self.enclosing_scope.get_symbols_in_this_scope())
        symbols.extend(self.get_symbols_in_this_scope())
        return symbols

    def get_scopes(self):
        """
        Returns the set of scopes as defined in this scope.
        :return: a list of scope objects
        :rtype: list
        """
        ret = list()
        for elem in self.declared_elements:
            if isinstance(elem, Scope):
                ret.append(elem)
        return ret

    def resolve_to_all_scopes(self, name, kind):
        """
        Resolves the handed over name and type and returns the scope in which the corresponding symbol has been defined.
        If element has been defined in several scopes, all scopes are returned as a list.
        :param name: the name of the element.
        :type name: str
        :param kind: the type of the element
        :type kind: SymbolKind
        :return: the scope in which the element has been defined in
        :rtype: Scope
        """
        g_scope = self.get_global_scope()
        scopes = g_scope.__resolve_to_scope_in_spanned_scope(name, kind)
        # the following step is done in order to return, whenever the list contains only one element, only this element
        if isinstance(scopes, list) and len(scopes) == 1:
            return scopes[0]
        elif isinstance(scopes, list) and len(scopes) == 0:
            return None
        else:
            return scopes

    def __resolve_to_scope_in_spanned_scope(self, name, kind):
        """
        Private method: returns this scope or one of the sub-scopes in which the handed over symbol is defined in.
        :param name: the name of the element.
        :type name: str
        :param kind: the type of the element
        :type kind: SymbolKind
        :return: the corresponding scope object.
        :rtype: Scope
        """
        ret = list()
        for sim in self.get_symbols_in_this_scope():
            if sim.get_symbol_name() == name and sim.get_symbol_kind() == kind:
                ret.append(self)
        for elem in self.get_scopes():  # otherwise check if it is in one of the sub-scopes
            temp = elem.__resolve_to_scope_in_spanned_scope(name, kind)
            if temp is not None:
                ret.extend(temp)
        return ret

    def resolve_to_all_symbols(self, name, kind):
        """
        Resolves the name and type and returns the corresponding symbol. Caution: Here, we also take redeclaration into
        account. This has to be prevented - if required - by cocos.
        If element has been defined in several scopes, all scopes are returned as a list.
        :param name: the name of the element.
        :type name: str
        :param kind: the type of the element
        :type kind: SymbolType
        :return: a single symbol element.
        :rtype: Symbol/list(Symbols)
        """
        g_scope = self.get_global_scope()
        symbols = g_scope.__resolve_to_symbol_in_spanned_scope(name, kind)
        # the following step is done in order to return, whenever the list contains only one element, only this element
        if isinstance(symbols, list) and len(symbols) == 1:
            return symbols[0]
        elif len(symbols) == 0:
            return None
        else:
            return symbols

    def __resolve_to_symbol_in_spanned_scope(self, name, kind):
        """
        Private method: returns a symbol if the handed over name and type belong to a symbol in this or one of the
        sub-scope. Caution: Here, we also take redeclaration into account. This has to be prevented - if required -
        by cocos.
        :param name: the name of the element.
        :type name: str
        :param kind: the type of the element
        :type kind: SymbolType
        :return: the corresponding symbol object.
        :rtype: list(Symbol)
        """
        ret = list()
        for sim in self.get_symbols_in_this_scope():
            if sim.get_symbol_name() == name and sim.get_symbol_kind() == kind:
                ret.append(sim)
        for elem in self.get_scopes():  # otherwise check if it is in one of the sub-scopes
            temp = elem.__resolve_to_symbol_in_spanned_scope(name, kind)
            if temp is not None:
                ret.extend(temp)
        return ret

    def resolve_to_scope(self, name, kind):
        """
        Returns the first scope (starting from this) in which the handed over symbol has been defined, i.e., starting
        from this, climbs recursively upwards unit the element has been located or no enclosing scope is left.
        :param name: the name of the symbol.
        :type name: str
        :param kind: the type of the symbol, i.e., Variable,function or type.
        :type kind: SymbolType
        :return: the first matching scope.
        :rtype: Scope.
        """
        for sim in self.get_symbols_in_this_scope():
            if sim.get_symbol_name() == name and sim.get_symbol_kind() == kind:
                return self
        if self.has_enclosing_scope():
            return self.get_enclosing_scope().resolve_to_symbol(name, kind)
        return None

    def resolve_to_symbol(self, name, kind):
        """
        Returns the first symbol corresponding to the handed over parameters, starting from this scope. Starting
        from this, climbs recursively upwards until the element has been located or no enclosing scope is left.
        :param name: the name of the symbol.
        :type name: str
        :param kind: the type of the symbol, i.e., Variable,function or type.
        :type kind: SymbolType
        :return: the first matching symbol.
        :rtype: variable_symbol or function_symbol
        """
        for sim in self.get_symbols_in_this_scope():
            if sim.get_symbol_name() == name and sim.get_symbol_kind() == kind:
                return sim
        if self.has_enclosing_scope():
            return self.get_enclosing_scope().resolve_to_symbol(name, kind)
        return None

    def get_global_scope(self):
        """
        Returns the GLOBAL scope in which all sub-scopes are embedded in.
        :return: the global scope element.
        :rtype: Scope
        """
        if self.get_scope_type() is ScopeType.GLOBAL:
            return self
        if self.has_enclosing_scope():
            return self.get_enclosing_scope().get_global_scope()
        return None

    def get_enclosing_scope(self):
        """
        Returns the enclosing scope if any is defined.
        :return: a scope symbol if available.
        :rtype: Scope
        """
        if self.enclosing_scope is not None:
            return self.enclosing_scope
        else:
            return None

    def has_enclosing_scope(self):
        """
        Returns this scope is embedded in a different scope.
        :return: True, if enclosed, otherwise False.
        :rtype: bool
        """
        return (self.enclosing_scope is not None) and (self.scope_type is not ScopeType.GLOBAL)

    def get_source_position(self):
        """
        Returns the position in the source as enclosed by this scope
        :return:
        :rtype:
        """
        return self.source_position

    def get_scope_type(self):
        """
        Returns the type of scope.
        :return: a ScopeType element.
        :rtype: ScopeType
        """
        return self.scope_type

    def is_enclosed_in(self, scope):
        """
        Returns if this scope is directly or indirectly enclosed in the handed over scope.
        :param scope: the scope in which this scope can be enclosed in.
        :type scope Scope
        :return: True, if this scope is directly or indirectly enclosed in the handed over one, otherwise False.
        :rtype: bool
        """
        if self.has_enclosing_scope() and self.get_enclosing_scope() is scope:
            return True
        elif self.has_enclosing_scope():
            return self.get_enclosing_scope().is_enclosed_in(scope)
        else:
            return False

    def get_depth_of_scope(self):
        """
        Returns the depth of this scope.
        :return: the level of encapsulation of this scope.
        :rtype: int
        """
        depth = 0
        if self.has_enclosing_scope():
            depth += 1 + self.get_enclosing_scope().get_depth_of_scope()
        return depth

    def print_scope(self):
        """
        Returns a string representation of symbol table as used for debug purpose.
        :return: a string representation of the scope and its sub-scope.
        :rtype: str
        """
        ret = ('-' * 2 * (self.get_depth_of_scope()))
        ret += '<' + self.get_scope_type().name + ',' + str(self.get_source_position()) + '>' + '\n'
        for elem in self.declared_elements:
            if isinstance(elem, Symbol):
                ret += ('-' * 2 * (self.get_depth_of_scope() + 1)) + elem.print_symbol() + '\n'
            else:
                ret += elem.print_scope()
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
