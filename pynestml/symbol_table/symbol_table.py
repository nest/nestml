# -*- coding: utf-8 -*-
#
# symbol_table.py
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
from pynestml.symbol_table.scope import Scope, ScopeType


class SymbolTable(object):
    """
    This class is used to store a single symbol table, consisting of scope and symbols.

    Attributes:
        name2neuron_scope A dict from the name of a neuron to the corresponding scope. Type str->Scope
        source_position The source position of the overall compilation unit. Type ASTSourceLocation
    """
    name2neuron_scope = {}
    source_location = None

    @classmethod
    def initialize_symbol_table(cls, source_position):
        """
        Standard initializer.
        """
        cls.source_location = source_position
        cls.name2neuron_scope = {}

    @classmethod
    def add_neuron_scope(cls, name, scope):
        """
        Adds a single neuron scope to the set of stored scopes.
        :return: a single scope element.
        :rtype: Scope
        """
        assert isinstance(scope, Scope), \
            '(PyNestML.SymbolTable.SymbolTable) No or wrong type of scope provided (%s)!' % type(scope)
        assert (scope.get_scope_type() == ScopeType.GLOBAL), \
            '(PyNestML.SymbolTable.SymbolTable) Only global scopes can be added!'
        assert isinstance(name, str), \
            '(PyNestML.SymbolTable.SymbolTable) No or wrong type of name provided (%s)!' % type(name)
        if name not in cls.name2neuron_scope.keys():
            cls.name2neuron_scope[name] = scope
        return

    @classmethod
    def delete_neuron_scope(cls, name):
        """
        Deletes a single neuron scope from the set of stored scopes.
        :return: the name of the scope to delete.
        :rtype: Scope
        """
        if name in cls.name2neuron_scope.keys():
            del cls.name2neuron_scope[name]
        return

    @classmethod
    def clean_up_table(cls):
        """
        Deletes all entries as stored in the symbol table.
        """
        del cls.name2neuron_scope
        cls.name2neuron_scope = {}

    @classmethod
    def print_symbol_table(cls):
        """
        Prints the content of this symbol table.
        """
        ret = ''
        for _name in cls.name2neuron_scope.keys():
            ret += '--------------------------------------------------\n'
            ret += _name + ':\n'
            ret += cls.name2neuron_scope[_name].print_scope()
        return ret
