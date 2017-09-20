#
# SymbolTable.py
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
from pynestml.src.main.python.org.nestml.symbol_table.Scope import Scope
from pynestml.src.main.python.org.nestml.symbol_table.Scope import ScopeType


class SymbolTable:
    """
    This class is used to store a single symbol table, consisting of scope and symbols.
    
    Attributes:
        __name2neuronScope A dict from the name of a neuron to the corresponding scope. Type str->Scope
        __sourcePosition The source position of the overall compilation unit. Type ASTSourcePosition
    """
    __name2neuronScope = {}
    __sourcePosition = None

    @classmethod
    def initializeSymbolTable(cls, _sourcePosition=None):
        """
        Standard initializer.
        """
        from pynestml.src.main.python.org.nestml.ast.ASTSourcePosition import ASTSourcePosition
        assert (_sourcePosition is not None and isinstance(_sourcePosition, ASTSourcePosition)), \
            '(PyNestML.SymbolTable.SymbolTable) No or wrong type of source position provided!'
        cls.__sourcePosition = _sourcePosition
        return

    @classmethod
    def addNeuronScope(cls, _name, _scope=None):
        """
        Adds a single neuron scope to the set of stored scopes.
        :return: a single scope element.
        :rtype: Scope
        """
        assert (_scope is not None and isinstance(_scope, Scope)), \
            '(PyNestML.SymbolTable.SymbolTable) No or wrong type of scope provided!'
        assert (_scope.getScopeType() == ScopeType.GLOBAL), \
            '(PyNestML.SymbolTable.SymbolTable) Only global scopes can be added!'
        assert (_name is not None and isinstance(_name, str)), \
            '(PyNestML.SymbolTable.SymbolTable) No or wrong type of name provided!'
        if _name not in cls.__name2neuronScope.keys():
            cls.__name2neuronScope[_name] = _scope
        return

    @classmethod
    def deleteNeuronScope(cls, _name=None):
        """
        Deletes a single neuron scope from the set of stored scopes.
        :return: the name of the scope to delete.
        :rtype: Scope
        """
        assert (_name is not None and isinstance(_name, Scope)), \
            '(PyNestML.SymbolTable.SymbolTable) No or wrong type of name provided!'
        if _name in cls.__name2neuronScope.keys():
            del cls.__name2neuronScope[_name]
        return

    @classmethod
    def printSymbolTable(cls):
        """
        Prints the content of this symbol table.
        """
        ret = ''
        for _name in cls.__name2neuronScope.keys():
            ret += '--------------------------------------------------\n'
            ret += _name + ':\n'
            ret += cls.__name2neuronScope[_name].printScope()
        return ret
