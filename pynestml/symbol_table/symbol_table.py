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

from typing import Dict

from pynestml.symbol_table.scope import Scope, ScopeType


class SymbolTable:
    r"""
    This class is used to store a single symbol table, consisting of scope and symbols.
    """
    name2model_scope: Dict[str, Scope] = {}    # A dict from the name of a model to the corresponding scope.
    source_location = None    # The source position of the overall compilation unit.

    @classmethod
    def initialize_symbol_table(cls, source_position):
        """
        Standard initializer.
        """
        cls.source_location = source_position
        cls.name2model_scope = {}

    @classmethod
    def add_model_scope(cls, name, scope) -> None:
        """
        Adds a single model scope to the set of stored scopes.
        """
        assert isinstance(scope, Scope), \
            "(PyNestML.SymbolTable.SymbolTable) No or wrong type of scope provided (%s)!" % type(scope)
        assert (scope.get_scope_type() == ScopeType.GLOBAL), \
            "(PyNestML.SymbolTable.SymbolTable) Only global scopes can be added!"
        assert isinstance(name, str), \
            "(PyNestML.SymbolTable.SymbolTable) No or wrong type of name provided (%s)!" % type(name)

        if name not in cls.name2model_scope.keys():
            cls.name2model_scope[name] = scope

    @classmethod
    def delete_model_scope(cls, name: str) -> None:
        """
        Deletes a single model scope from the set of stored scopes.
        :param name: the name of the scope to delete.
        """
        if name in cls.name2model_scope.keys():
            del cls.name2model_scope[name]

    @classmethod
    def clean_up_table(cls):
        """
        Deletes all entries as stored in the symbol table.
        """
        del cls.name2model_scope
        cls.name2model_scope = {}

    @classmethod
    def print_symbol_table(cls) -> str:
        """
        Prints the content of this symbol table.
        """
        ret = ""
        for _name in cls.name2model_scope.keys():
            ret += "--------------------------------------------------\n"
            ret += _name + ":\n"
            ret += cls.name2model_scope[_name].print_scope()
        return ret
